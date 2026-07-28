"""
Metrics collection and analysis for chaos experiments
"""

import docker
import requests
import time
import statistics
from typing import Dict, Any, List
from datetime import datetime


class MetricsCollector:
    """
    Collects and analyzes system metrics during chaos experiments
    """
    
    def __init__(self, service_name: str = None):
        self.service_name = service_name
        self.client = docker.from_env()
        self.config = self._load_config()
        self.gateway_url = self.config.get('gateway_url', 'http://localhost:8000')
        
    def _load_config(self):
        """Load configuration"""
        from chaos_monkey.utils.config import Config
        return Config()
    
    def collect_baseline(self) -> Dict[str, Any]:
        """Collect baseline metrics before attack"""
        if self.service_name:
            return self._collect_service_metrics(self.service_name)
        return self._collect_system_metrics()
    
    def monitor_during_attack(self, duration_seconds: int, attack_instance) -> Dict[str, Any]:
        """Monitor metrics during the attack"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration_seconds,
            'samples': [],
            'error_count': 0,
            'total_requests': 0,
            'latencies': [],
            'availability_samples': []
        }
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        sample_interval = 2  # Sample every 2 seconds
        
        while time.time() < end_time:
            try:
                sample = self._collect_service_metrics(self.service_name)
                metrics['samples'].append(sample)
                metrics['latencies'].append(sample.get('latency_ms', 0))
                metrics['availability_samples'].append(sample.get('availability', 100))
                metrics['total_requests'] += 1
                
                if sample.get('status') != 'healthy':
                    metrics['error_count'] += 1
                    
            except Exception as e:
                metrics['error_count'] += 1
            
            time.sleep(sample_interval)
        
        # Calculate aggregates
        if metrics['latencies']:
            metrics['avg_latency'] = statistics.mean(metrics['latencies'])
            metrics['max_latency'] = max(metrics['latencies'])
            metrics['min_latency'] = min(metrics['latencies'])
        
        if metrics['availability_samples']:
            metrics['avg_availability'] = statistics.mean(metrics['availability_samples'])
        
        metrics['error_rate'] = (metrics['error_count'] / metrics['total_requests'] * 100) if metrics['total_requests'] > 0 else 0
        
        return metrics
    
    def collect_final(self) -> Dict[str, Any]:
        """Collect final metrics after attack and recovery"""
        if self.service_name:
            return self._collect_service_metrics(self.service_name)
        return self._collect_system_metrics()
    
    def measure_recovery_time(self) -> float:
        """Measure time taken for system to recover after attack"""
        recovery_start = time.time()
        max_recovery_time = 300  # 5 minutes max
        
        while time.time() - recovery_start < max_recovery_time:
            try:
                metrics = self._collect_service_metrics(self.service_name)
                
                # Consider recovered if:
                # - Status is healthy
                # - Latency is within acceptable range (2x baseline)
                # - Availability is > 99%
                
                if (metrics.get('status') == 'healthy' and 
                    metrics.get('availability', 0) > 99 and
                    metrics.get('latency_ms', 0) < 1000):  # 1 second threshold
                    recovery_time = time.time() - recovery_start
                    print(f"System recovered in {recovery_time:.2f} seconds")
                    return recovery_time
                
            except Exception as e:
                pass
            
            time.sleep(2)
        
        # If not recovered within max time
        print(f"System did not recover within {max_recovery_time} seconds")
        return max_recovery_time
    
    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health status of a specific service"""
        return self._collect_service_metrics(service_name)
    
    def _collect_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Collect metrics for a specific service"""
        try:
            service_config = self.config.get(f'services.{service_name}')
            if not service_config:
                return {'status': 'unknown', 'error': 'Service not configured'}
            
            port = service_config.get('port')
            if not port:
                return {'status': 'unknown', 'error': 'Port not configured'}
            
            # Try direct health check
            health_url = f"http://localhost:{port}/health"
            
            start_time = time.time()
            response = requests.get(health_url, timeout=5)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'latency_ms': round(latency_ms, 2),
                    'availability': 100,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'latency_ms': round(latency_ms, 2),
                    'availability': 0,
                    'error_code': response.status_code,
                    'timestamp': datetime.now().isoformat()
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'latency_ms': 5000,
                'availability': 0,
                'error': 'Request timeout',
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'unreachable',
                'latency_ms': 0,
                'availability': 0,
                'error': 'Connection refused',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'latency_ms': 0,
                'availability': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect overall system metrics via gateway"""
        try:
            response = requests.get(f"{self.gateway_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Calculate overall availability
                healthy_count = sum(1 for s in data.get('services', []) if s.get('status') == 'healthy')
                total_count = len(data.get('services', []))
                availability = (healthy_count / total_count * 100) if total_count > 0 else 0
                
                return {
                    'status': data.get('overall_status', 'unknown'),
                    'availability': round(availability, 2),
                    'services': data.get('services', []),
                    'uptime': data.get('uptime', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'availability': 0,
                    'error': f'Gateway returned {response.status_code}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'availability': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_container_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get Docker container metrics"""
        try:
            service_config = self.config.get(f'services.{service_name}')
            if not service_config:
                return {'status': 'not_found', 'error': f'Service {service_name} not configured'}
            
            container_name = service_config.get('container')
            container = self.client.containers.get(container_name)
            
            stats = container.stats(stream=False)
            
            # Calculate CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0
            
            # Get memory usage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                'memory_percent': round(memory_percent, 2),
                'status': container.status,
                'timestamp': datetime.now().isoformat()
            }
            
        except docker.errors.NotFound:
            return {'status': 'not_found', 'error': f'Container {service_name} not found'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
