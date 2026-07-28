"""
Configuration and utility functions
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration management for ChaosMonkey-Lite"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Check for config in current directory
        local_config = Path('./chaos-config.yaml')
        if local_config.exists():
            return str(local_config)
        
        # Check for config in home directory
        home_config = Path.home() / '.chaos-monkey' / 'config.yaml'
        if home_config.exists():
            return str(home_config)
        
        # Return default config path
        return str(Path(__file__).parent.parent.parent / 'config' / 'default.yaml')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            return self._get_default_config()
        
        try:
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except ImportError:
            # Fallback to JSON if yaml not available
            with open(config_file, 'r') as f:
                return json.load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'gateway_url': 'http://localhost:8000',
            'default_duration': 30,
            'default_latency': 5000,
            'auto_restart': True,
            'safety_checks': True,
            'max_duration': 300,
            'critical_services': ['auth', 'gateway'],
            'metrics': {
                'sample_interval': 2,
                'recovery_timeout': 300
            },
            'logging': {
                'level': 'INFO',
                'file': 'chaos-monkey.log'
            },
            'services': {}
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except ImportError:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds"""
    duration_str = duration_str.lower().strip()
    
    if duration_str.endswith('s'):
        return int(duration_str[:-1])
    elif duration_str.endswith('m'):
        return int(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        return int(duration_str[:-1]) * 3600
    elif duration_str.endswith('ms'):
        return int(duration_str[:-2]) / 1000
    else:
        return int(duration_str)


def parse_latency(latency_str: str) -> int:
    """Parse latency string to milliseconds"""
    latency_str = latency_str.lower().strip()
    
    if latency_str.endswith('ms'):
        return int(latency_str[:-2])
    elif latency_str.endswith('s'):
        return int(latency_str[:-1]) * 1000
    else:
        return int(latency_str)


def format_duration(seconds: int) -> str:
    """Format seconds to human-readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_latency(milliseconds: int) -> str:
    """Format milliseconds to human-readable latency"""
    if milliseconds < 1000:
        return f"{milliseconds}ms"
    else:
        seconds = milliseconds / 1000
        return f"{seconds:.2f}s"


def ensure_directory(path: str):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_service_container_name(service: str) -> str:
    """Get Docker container name for a service from configuration"""
    from chaos_monkey.utils.config import Config
    config = Config()
    service_config = config.get(f'services.{service}')
    if service_config:
        return service_config.get('container', f"{service}-service")
    return f"{service}-service"


def get_service_port(service: str) -> int:
    """Get port for a service from configuration"""
    from chaos_monkey.utils.config import Config
    config = Config()
    service_config = config.get(f'services.{service}')
    if service_config:
        return service_config.get('port', 8000)
    return 8000
