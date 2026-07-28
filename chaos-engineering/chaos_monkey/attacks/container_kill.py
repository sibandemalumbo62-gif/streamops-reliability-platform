"""
Container kill attack mechanism
"""

import docker
import time
from typing import Dict, Any


class ContainerKillAttack:
    """
    Kills and optionally restarts a Docker container to simulate service failure
    """
    
    def __init__(self, service_name: str, auto_restart: bool = True):
        self.service_name = service_name
        self.auto_restart = auto_restart
        self.client = docker.from_env()
        self.container = None
        self.original_state = None
        self.kill_time = None
        
    def execute(self):
        """Execute container kill attack"""
        try:
            # Find the target container from configuration
            from chaos_monkey.utils.config import Config
            config = Config()
            service_config = config.get(f'services.{self.service_name}')
            
            if not service_config:
                raise Exception(f"Service {self.service_name} not found in configuration")
            
            container_name = service_config.get('container')
            self.container = self.client.containers.get(container_name)
            
            # Store original state
            self.original_state = {
                'status': self.container.status,
                'restart_policy': self.container.restart_policy.get('Name') if self.container.restart_policy else None
            }
            
            print(f"Killing container: {container_name}")
            
            # Kill the container
            self.kill_time = time.time()
            self.container.kill()
            
            # Wait to confirm it's stopped
            self.container.wait(timeout=10)
            
            print(f"Container {container_name} killed successfully")
            
            # Auto-restart if enabled
            if self.auto_restart:
                print(f"Auto-restarting container...")
                time.sleep(2)  # Brief delay before restart
                self.container.restart()
                print(f"Container {container_name} restarted")
            
            return True
            
        except docker.errors.NotFound:
            raise Exception(f"Container {container_name} not found")
        except Exception as e:
            raise Exception(f"Failed to kill container: {str(e)}")
    
    def rollback(self):
        """Rollback container kill by ensuring it's running"""
        try:
            if not self.container:
                return
            
            # Check if container is running
            self.container.reload()
            
            if self.container.status != 'running':
                print(f"Rolling back: Starting container {self.container.name}")
                self.container.start()
                print(f"Container {self.container.name} started")
            else:
                print(f"Container {self.container.name} is already running")
                
        except Exception as e:
            print(f"Error during rollback: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current attack status"""
        if not self.container:
            return {'status': 'not_executed'}
        
        try:
            self.container.reload()
            return {
                'status': self.container.status,
                'service': self.service_name,
                'auto_restart': self.auto_restart,
                'kill_time': self.kill_time,
                'downtime_seconds': time.time() - self.kill_time if self.kill_time else 0
            }
        except:
            return {'status': 'unknown', 'service': self.service_name}
