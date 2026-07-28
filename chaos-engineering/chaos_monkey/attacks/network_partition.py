"""
Network partition attack mechanism
"""

import docker
import time
from typing import Dict, Any


class NetworkPartitionAttack:
    """
    Simulates network partition by blocking network traffic between services
    """
    
    def __init__(self, service_name: str, target_service: str, duration_seconds: int):
        self.service_name = service_name
        self.target_service = target_service
        self.duration_seconds = duration_seconds
        self.client = docker.from_env()
        self.source_container = None
        self.target_container = None
        self.original_network_config = None
        
    def execute(self):
        """Execute network partition attack"""
        try:
            # Find containers from configuration
            from chaos_monkey.utils.config import Config
            config = Config()
            
            source_config = config.get(f'services.{self.service_name}')
            target_config = config.get(f'services.{self.target_service}')
            
            if not source_config:
                raise Exception(f"Service {self.service_name} not found in configuration")
            if not target_config:
                raise Exception(f"Service {self.target_service} not found in configuration")
            
            source_container_name = source_config.get('container')
            self.source_container = self.client.containers.get(source_container_name)
            
            target_container_name = target_config.get('container')
            self.target_container = self.client.containers.get(target_container_name)
            
            print(f"Creating network partition between {source_container_name} and {target_container_name}")
            
            # Store original network configuration
            self.original_network_config = {
                'source_networks': self.source_container.attrs['NetworkSettings']['Networks'],
                'target_networks': self.target_container.attrs['NetworkSettings']['Networks']
            }
            
            # Method: Disconnect containers from the shared network temporarily
            # Get the network they share
            shared_network = None
            for network_name, network_config in self.source_container.attrs['NetworkSettings']['Networks'].items():
                if network_name in self.target_container.attrs['NetworkSettings']['Networks']:
                    shared_network = self.client.networks.get(network_name)
                    break
            
            if shared_network:
                print(f"Disconnecting {source_container_name} from network {shared_network.name}")
                shared_network.disconnect(self.source_container)
                
                print(f"Network partition active for {self.duration_seconds} seconds")
                
                # Wait for the duration
                time.sleep(self.duration_seconds)
                
                # Reconnect
                print(f"Reconnecting {source_container_name} to network {shared_network.name}")
                shared_network.connect(self.source_container)
                
            else:
                raise Exception("No shared network found between containers")
            
            return True
            
        except docker.errors.NotFound as e:
            raise Exception(f"Container not found: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create network partition: {str(e)}")
    
    def rollback(self):
        """Rollback network partition"""
        try:
            if self.source_container and self.original_network_config:
                print(f"Rolling back: Ensuring network connectivity restored")
                
                # Ensure container is reconnected to original networks
                shared_network = None
                for network_name in self.original_network_config['source_networks'].keys():
                    try:
                        network = self.client.networks.get(network_name)
                        # Check if container is connected
                        if network_name not in self.source_container.attrs['NetworkSettings']['Networks']:
                            network.connect(self.source_container)
                    except:
                        pass
                
                print(f"Network partition rolled back")
                
        except Exception as e:
            print(f"Error during rollback: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current attack status"""
        if not self.source_container:
            return {'status': 'not_executed'}
        
        try:
            self.source_container.reload()
            return {
                'status': 'rolled_back',  # Network partition is temporary
                'service': self.service_name,
                'target': self.target_service,
                'duration': self.duration_seconds
            }
        except:
            return {'status': 'unknown', 'service': self.service_name}
