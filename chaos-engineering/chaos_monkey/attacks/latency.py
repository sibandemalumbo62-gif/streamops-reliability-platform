"""
Latency injection attack mechanism
"""

import docker
import time
import requests
from typing import Dict, Any


class LatencyAttack:
    """
    Injects artificial latency into a service by modifying its network configuration
    or using intermediate proxy to delay requests
    """
    
    def __init__(self, service_name: str, latency_ms: int, duration_seconds: int):
        self.service_name = service_name
        self.latency_ms = latency_ms
        self.duration_seconds = duration_seconds
        self.client = docker.from_env()
        self.original_config = None
        self.container = None
        
    def execute(self):
        """Execute latency injection attack"""
        try:
            # Find the target container from configuration
            from chaos_monkey.utils.config import Config
            config = Config()
            service_config = config.get(f'services.{self.service_name}')
            
            if not service_config:
                raise Exception(f"Service {self.service_name} not found in configuration")
            
            container_name = service_config.get('container')
            self.container = self.client.containers.get(container_name)
            
            # Store original configuration
            self.original_config = {
                'status': self.container.status,
                'labels': self.container.labels
            }
            
            # Inject latency using tc (traffic control) if available
            # For Docker, we'll use a different approach: pause/resume cycles
            # to simulate latency
            
            self._inject_latency_via_pause()
            
            return True
            
        except docker.errors.NotFound:
            raise Exception(f"Container {container_name} not found")
        except Exception as e:
            raise Exception(f"Failed to inject latency: {str(e)}")
    
    def _inject_latency_via_pause(self):
        """
        Inject latency by periodically pausing and resuming the container
        This simulates network latency without requiring tc inside the container
        """
        print(f"Injecting {self.latency_ms}ms latency into {self.service_name}")
        
        # Calculate pause intervals to simulate latency
        # For every request, pause for latency_ms / 2
        pause_interval = self.latency_ms / 2000  # Convert to seconds
        
        start_time = time.time()
        end_time = start_time + self.duration_seconds
        
        while time.time() < end_time:
            # Pause container
            self.container.pause()
            time.sleep(pause_interval)
            
            # Resume container
            self.container.unpause()
            time.sleep(pause_interval)
    
    def rollback(self):
        """Rollback latency injection"""
        try:
            if self.container:
                # Ensure container is running
                self.container.unpause()
                print(f"Rolled back latency injection for {self.service_name}")
                
        except Exception as e:
            print(f"Error during rollback: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current attack status"""
        if not self.container:
            return {'status': 'not_executed'}
        
        return {
            'status': 'active' if self.container.status == 'paused' else 'rolled_back',
            'service': self.service_name,
            'latency_ms': self.latency_ms,
            'duration_remaining': max(0, self.duration_seconds - (time.time() - getattr(self, 'start_time', 0)))
        }
