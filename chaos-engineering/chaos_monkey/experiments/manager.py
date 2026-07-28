"""
Experiment configuration and management
"""

import yaml
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from chaos_monkey.attacks.latency import LatencyAttack
from chaos_monkey.attacks.container_kill import ContainerKillAttack
from chaos_monkey.attacks.database_drop import DatabaseDropAttack
from chaos_monkey.attacks.network_partition import NetworkPartitionAttack
from chaos_monkey.metrics.collector import MetricsCollector
from chaos_monkey.safety.guards import SafetyGuards


class ExperimentManager:
    """
    Manages chaos experiments from configuration files
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.experiment_id = config.get('id', f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.safety = SafetyGuards()
        
    def run_experiment(self) -> Dict[str, Any]:
        """Run a complete chaos experiment from configuration"""
        print(f"🧪 Running experiment: {self.experiment_id}")
        print(f"📋 Description: {self.config.get('description', 'No description')}")
        
        # Validate configuration
        if not self.safety.validate_experiment_config(self.config):
            return {
                'id': self.experiment_id,
                'status': 'failed',
                'reason': 'Configuration validation failed'
            }
        
        # Pre-flight checks
        service = self.config.get('service')
        if not self.safety.pre_flight_check(service):
            return {
                'id': self.experiment_id,
                'status': 'failed',
                'reason': 'Pre-flight checks failed'
            }
        
        # Initialize metrics collector
        metrics = MetricsCollector(service)
        
        # Collect baseline
        print("📊 Collecting baseline metrics...")
        baseline = metrics.collect_baseline()
        
        # Execute attack sequence
        results = {
            'id': self.experiment_id,
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'baseline_metrics': baseline,
            'phases': [],
            'status': 'running'
        }
        
        try:
            # Execute each phase
            for phase in self.config.get('phases', []):
                phase_result = self._execute_phase(phase, metrics)
                results['phases'].append(phase_result)
                
                if phase_result.get('status') == 'failed':
                    results['status'] = 'failed'
                    break
            
            # Collect final metrics
            print("📊 Collecting final metrics...")
            final_metrics = metrics.collect_final()
            results['final_metrics'] = final_metrics
            
            # Calculate overall recovery time
            total_recovery_time = sum(
                phase.get('recovery_time', 0) 
                for phase in results['phases']
            )
            results['recovery_time'] = total_recovery_time
            
            results['status'] = 'completed'
            
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)
            print(f"❌ Experiment failed: {str(e)}")
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _execute_phase(self, phase: Dict[str, Any], metrics: MetricsCollector) -> Dict[str, Any]:
        """Execute a single phase of the experiment"""
        phase_name = phase.get('name', 'unnamed')
        print(f"\n🎯 Executing phase: {phase_name}")
        
        phase_result = {
            'name': phase_name,
            'status': 'running',
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Get attack parameters
            service = self.config.get('service')
            failure_type = phase.get('failure')
            duration = phase.get('duration', 30)
            
            # Create attack instance
            attack_instance = self._create_attack(service, failure_type, phase)
            
            # Execute attack
            print(f"💥 Injecting {failure_type}...")
            attack_instance.execute()
            
            # Monitor during attack
            print(f"⏳ Monitoring for {duration}s...")
            attack_metrics = metrics.monitor_during_attack(duration, attack_instance)
            
            # Rollback
            print(f"🔄 Rolling back...")
            attack_instance.rollback()
            
            # Measure recovery
            print(f"⏱️  Measuring recovery...")
            recovery_time = metrics.measure_recovery_time()
            
            phase_result.update({
                'status': 'completed',
                'attack_metrics': attack_metrics,
                'recovery_time': recovery_time,
                'end_time': datetime.now().isoformat()
            })
            
            print(f"✅ Phase {phase_name} completed (recovery: {recovery_time}s)")
            
        except Exception as e:
            phase_result.update({
                'status': 'failed',
                'error': str(e),
                'end_time': datetime.now().isoformat()
            })
            print(f"❌ Phase {phase_name} failed: {str(e)}")
        
        return phase_result
    
    def _create_attack(self, service: str, failure_type: str, phase: Dict[str, Any]):
        """Create attack instance based on type"""
        duration = phase.get('duration', 30)
        
        if failure_type == 'latency':
            latency_ms = phase.get('latency_ms', 5000)
            return LatencyAttack(service, latency_ms, duration)
        
        elif failure_type == 'kill':
            auto_restart = phase.get('auto_restart', True)
            return ContainerKillAttack(service, auto_restart)
        
        elif failure_type == 'database-drop':
            return DatabaseDropAttack(service, duration)
        
        elif failure_type == 'network-partition':
            target = phase.get('target')
            return NetworkPartitionAttack(service, target, duration)
        
        else:
            raise ValueError(f"Unknown failure type: {failure_type}")
    
    def _save_results(self, results: Dict[str, Any]):
        """Save experiment results to file"""
        results_dir = Path('experiments/results')
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = results_dir / f"{self.experiment_id}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to {results_file}")


class ExperimentLoader:
    """Load and validate experiment configurations"""
    
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """Load experiment configuration from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Experiment file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif file_path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    @staticmethod
    def list_available_experiments() -> List[Dict[str, Any]]:
        """List all available experiment configurations"""
        experiments_dir = Path('experiments/configs')
        experiments = []
        
        if not experiments_dir.exists():
            return experiments
        
        for config_file in experiments_dir.glob('*.yaml'):
            try:
                config = ExperimentLoader.load_from_file(config_file)
                experiments.append({
                    'file': config_file.name,
                    'id': config.get('id'),
                    'name': config.get('name'),
                    'description': config.get('description'),
                    'service': config.get('service')
                })
            except:
                continue
        
        return experiments
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate experiment configuration"""
        errors = []
        
        # Required fields
        required_fields = ['service', 'phases']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate service exists in config
        from chaos_monkey.utils.config import Config
        app_config = Config()
        valid_services = list(app_config.get('services', {}).keys())
        
        if config.get('service') not in valid_services:
            errors.append(f"Invalid service: {config.get('service')}. Valid services: {valid_services}")
        
        # Validate phases
        phases = config.get('phases', [])
        if not phases:
            errors.append("No phases defined")
        
        for i, phase in enumerate(phases):
            if 'failure' not in phase:
                errors.append(f"Phase {i}: Missing failure type")
            
            valid_failures = ['latency', 'kill', 'database-drop', 'network-partition']
            if phase.get('failure') not in valid_failures:
                errors.append(f"Phase {i}: Invalid failure type: {phase.get('failure')}")
        
        return len(errors) == 0, errors
