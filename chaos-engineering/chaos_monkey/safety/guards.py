"""
Safety guards and rollback mechanisms for chaos experiments
"""

import docker
import requests
from typing import Dict, Any, List


class SafetyGuards:
    """
    Implements safety checks to prevent chaos experiments from causing
    irreversible damage to the system
    """
    
    def __init__(self):
        self.client = docker.from_env()
        self.config = self._load_config()
        self.gateway_url = self.config.get('gateway_url', 'http://localhost:8000')
        
        # Safety thresholds
        self.thresholds = {
            'min_healthy_services': self.config.get('safety.min_healthy_services', 3),
            'max_error_rate': self.config.get('safety.max_error_rate', 50),
            'max_latency_ms': self.config.get('safety.max_latency_ms', 10000),
            'critical_services': self.config.get('critical_services', ['auth', 'gateway'])
        }
    
    def _load_config(self):
        """Load configuration"""
        from chaos_monkey.utils.config import Config
        return Config()
    
    def pre_flight_check(self, service_name: str) -> bool:
        """
        Perform pre-flight checks before executing chaos attack
        Returns True if safe to proceed, False otherwise
        """
        print("🔍 Running pre-flight safety checks...")
        
        checks = [
            self._check_system_health,
            self._check_service_availability,
            self._check_critical_services,
            self._check_recent_failures,
            self._check_resource_availability
        ]
        
        results = []
        for check in checks:
            try:
                result = check(service_name)
                results.append(result)
                if not result['passed']:
                    print(f"❌ Check failed: {result['name']} - {result['reason']}")
                else:
                    print(f"✅ Check passed: {result['name']}")
            except Exception as e:
                print(f"⚠️  Check error: {check.__name__} - {str(e)}")
                results.append({'passed': False, 'name': check.__name__, 'reason': str(e)})
        
        # All checks must pass
        all_passed = all(result['passed'] for result in results)
        
        if all_passed:
            print("✅ All pre-flight checks passed")
        else:
            print("❌ Pre-flight checks failed - aborting attack")
        
        return all_passed
    
    def _check_system_health(self, service_name: str) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            response = requests.get(f"{self.gateway_url}/health", timeout=5)
            
            if response.status_code != 200:
                return {
                    'passed': False,
                    'name': 'System Health',
                    'reason': f'Gateway unhealthy: {response.status_code}'
                }
            
            data = response.json()
            overall_status = data.get('overall_status')
            
            if overall_status != 'healthy':
                return {
                    'passed': False,
                    'name': 'System Health',
                    'reason': f'System status: {overall_status}'
                }
            
            return {'passed': True, 'name': 'System Health'}
            
        except Exception as e:
            return {
                'passed': False,
                'name': 'System Health',
                'reason': f'Cannot check system health: {str(e)}'
            }
    
    def _check_service_availability(self, service_name: str) -> Dict[str, Any]:
        """Check if target service is available"""
        try:
            service_config = self.config.get(f'services.{service_name}')
            if not service_config:
                return {
                    'passed': False,
                    'name': 'Service Availability',
                    'reason': f'Service {service_name} not configured'
                }
            
            container_name = service_config.get('container')
            container = self.client.containers.get(container_name)
            
            if container.status != 'running':
                return {
                    'passed': False,
                    'name': 'Service Availability',
                    'reason': f'Service {service_name} is not running (status: {container.status})'
                }
            
            return {'passed': True, 'name': 'Service Availability'}
            
        except docker.errors.NotFound:
            return {
                'passed': False,
                'name': 'Service Availability',
                'reason': f'Service {service_name} container not found'
            }
        except Exception as e:
            return {
                'passed': False,
                'name': 'Service Availability',
                'reason': str(e)
            }
    
    def _check_critical_services(self, service_name: str) -> Dict[str, Any]:
        """Ensure critical services are healthy"""
        try:
            response = requests.get(f"{self.gateway_url}/health", timeout=5)
            data = response.json()
            
            services = data.get('services', [])
            
            for critical_service in self.thresholds['critical_services']:
                if critical_service == service_name:
                    continue  # Skip if this is the target service
                
                service_health = next(
                    (s for s in services if s['service'] == critical_service),
                    None
                )
                
                if not service_health or service_health.get('status') != 'healthy':
                    return {
                        'passed': False,
                        'name': 'Critical Services',
                        'reason': f'Critical service {critical_service} is unhealthy'
                    }
            
            return {'passed': True, 'name': 'Critical Services'}
            
        except Exception as e:
            return {
                'passed': False,
                'name': 'Critical Services',
                'reason': str(e)
            }
    
    def _check_recent_failures(self, service_name: str) -> Dict[str, Any]:
        """Check if there have been recent failures"""
        try:
            service_config = self.config.get(f'services.{service_name}')
            if not service_config:
                return {'passed': True, 'name': 'Recent Failures'}  # Skip if not configured
            
            container_name = service_config.get('container')
            container = self.client.containers.get(container_name)
            
            # Check if container has restarted recently
            restart_count = container.attrs.get('RestartCount', 0)
            
            if restart_count > 5:
                return {
                    'passed': False,
                    'name': 'Recent Failures',
                    'reason': f'Service has restarted {restart_count} times recently'
                }
            
            return {'passed': True, 'name': 'Recent Failures'}
            
        except Exception as e:
            return {
                'passed': False,
                'name': 'Recent Failures',
                'reason': str(e)
            }
    
    def _check_resource_availability(self, service_name: str) -> Dict[str, Any]:
        """Check system resource availability"""
        try:
            import psutil
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                return {
                    'passed': False,
                    'name': 'Resource Availability',
                    'reason': f'High CPU usage: {cpu_percent}%'
                }
            
            # Check memory usage
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:
                return {
                    'passed': False,
                    'name': 'Resource Availability',
                    'reason': f'High memory usage: {memory_percent}%'
                }
            
            # Check disk usage
            disk_percent = psutil.disk_usage('/').percent
            if disk_percent > 90:
                return {
                    'passed': False,
                    'name': 'Resource Availability',
                    'reason': f'High disk usage: {disk_percent}%'
                }
            
            return {'passed': True, 'name': 'Resource Availability'}
            
        except ImportError:
            # psutil not available, skip this check
            return {'passed': True, 'name': 'Resource Availability', 'reason': 'psutil not available'}
        except Exception as e:
            return {
                'passed': False,
                'name': 'Resource Availability',
                'reason': str(e)
            }
    
    def emergency_rollback(self, service_name: str):
        """Emergency rollback in case of critical failure"""
        print(f"🚨 EMERGENCY ROLLBACK for {service_name}")
        
        try:
            # Ensure all critical services are running
            for critical_service in self.thresholds['critical_services']:
                service_config = self.config.get(f'services.{critical_service}')
                if service_config:
                    container_name = service_config.get('container')
                    try:
                        container = self.client.containers.get(container_name)
                        if container.status != 'running':
                            container.start()
                            print(f"✅ Restarted critical service: {critical_service}")
                    except:
                        print(f"⚠️  Could not restart critical service: {critical_service}")
            
            # Ensure target service is running
            service_config = self.config.get(f'services.{service_name}')
            if service_config:
                container_name = service_config.get('container')
                try:
                    container = self.client.containers.get(container_name)
                    if container.status != 'running':
                        container.start()
                        print(f"✅ Restarted target service: {service_name}")
                except:
                    print(f"⚠️  Could not restart target service: {service_name}")
            
            print("🚨 Emergency rollback completed")
            
        except Exception as e:
            print(f"❌ Emergency rollback failed: {str(e)}")
    
    def validate_experiment_config(self, config: Dict[str, Any]) -> bool:
        """Validate experiment configuration for safety"""
        # Check duration limits
        duration = config.get('duration', 30)
        max_duration = self.config.get('max_duration', 300)
        if duration > max_duration:
            print(f"❌ Duration too long: {duration}s (max: {max_duration}s)")
            return False
        
        # Check if target is a critical service
        target = config.get('service')
        if target in self.thresholds['critical_services']:
            print(f"⚠️  Targeting critical service: {target}")
            # Allow but warn
        
        # Check failure type
        failure_type = config.get('failure')
        dangerous_failures = ['network-partition', 'database-drop']
        if failure_type in dangerous_failures:
            print(f"⚠️  Dangerous failure type: {failure_type}")
        
        return True
