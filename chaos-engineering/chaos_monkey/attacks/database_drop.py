"""
Database connection drop attack mechanism
"""

import docker
import time
import requests
from typing import Dict, Any


class DatabaseDropAttack:
    """
    Simulates database connection failures by blocking network access
    between the service and its database
    """
    
    def __init__(self, service_name: str, duration_seconds: int):
        self.service_name = service_name
        self.duration_seconds = duration_seconds
        self.client = docker.from_env()
        self.service_container = None
        self.db_container = None
        self.original_network_config = None
    
    def execute(self):
        """Execute database connection drop attack"""
        try:
            # Find the service and database containers from configuration
            from chaos_monkey.utils.config import Config
            config = Config()
            service_config = config.get(f'services.{self.service_name}')
            
            if not service_config:
                raise Exception(f"Service {self.service_name} not found in configuration")
            
            service_container_name = service_config.get('container')
            self.service_container = self.client.containers.get(service_container_name)
            
            # Find the database container
            db_container_name = service_config.get('database')
            if not db_container_name:
                raise Exception(f"No database configured for service {self.service_name}")
            
            self.db_container = self.client.containers.get(db_container_name)
            
            print(f"Dropping database connection between {service_container_name} and {db_container_name}")
            
            # Store original network configuration
            self.original_network_config = {
                'service_networks': self.service_container.attrs['NetworkSettings']['Networks'],
                'db_networks': self.db_container.attrs['NetworkSettings']['Networks']
            }
            
            # Method 1: Pause database container (simulates db failure)
            print(f"Pausing database container...")
            self.db_container.pause()
            
            print(f"Database connection dropped for {self.duration_seconds} seconds")
            
            # Wait for the duration
            time.sleep(self.duration_seconds)
            
            return True
            
        except docker.errors.NotFound as e:
            raise Exception(f"Container not found: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to drop database connection: {str(e)}")
    
    def rollback(self):
        """Rollback database connection drop"""
        try:
            if self.db_container:
                print(f"Rolling back: Resuming database container")
                self.db_container.unpause()
                print(f"Database connection restored")
                
        except Exception as e:
            print(f"Error during rollback: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current attack status"""
        if not self.db_container:
            return {'status': 'not_executed'}
        
        try:
            self.db_container.reload()
            from chaos_monkey.utils.config import Config
            config = Config()
            service_config = config.get(f'services.{self.service_name}')
            db_container_name = service_config.get('database') if service_config else 'unknown'
            
            return {
                'status': 'active' if self.db_container.status == 'paused' else 'rolled_back',
                'service': self.service_name,
                'database': db_container_name,
                'duration_remaining': max(0, self.duration_seconds - (time.time() - getattr(self, 'start_time', 0)))
            }
        except:
            return {'status': 'unknown', 'service': self.service_name}
