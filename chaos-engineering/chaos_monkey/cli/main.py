"""
Main CLI interface for ChaosMonkey-Lite
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from datetime import datetime
import json
import yaml

from chaos_monkey.attacks.latency import LatencyAttack
from chaos_monkey.attacks.container_kill import ContainerKillAttack
from chaos_monkey.attacks.database_drop import DatabaseDropAttack
from chaos_monkey.attacks.network_partition import NetworkPartitionAttack
from chaos_monkey.metrics.collector import MetricsCollector
from chaos_monkey.safety.guards import SafetyGuards
from chaos_monkey.experiments.manager import ExperimentManager
from chaos_monkey.utils.config import Config

console = Console()


@click.group()
@click.version_option(version='1.0.0', prog_name='chaos-monkey-lite')
def cli():
    """
    🐒 ChaosMonkey-Lite - Chaos Engineering Framework
    
    A production-grade chaos engineering framework for distributed systems.
    """
    pass


@cli.command()
@click.option('--service', required=True, help='Target service name (configured in config/default.yaml)')
@click.option('--failure', required=True, 
              type=click.Choice(['latency', 'kill', 'database-drop', 'network-partition']),
              help='Type of failure to inject')
@click.option('--duration', default='30s', help='Duration of the attack (e.g., 30s, 5m)')
@click.option('--latency', default='5000ms', help='Latency to inject (e.g., 5000ms, 2s)')
@click.option('--target', help='Target for network partition (e.g., database)')
@click.option('--auto-restart', is_flag=True, help='Automatically restart killed containers')
@click.option('--force', is_flag=True, help='Skip safety checks (use with caution)')
def attack(service, failure, duration, latency, target, auto_restart, force):
    """
    Execute a chaos attack on a service
    
    Example:
        chaos attack --service api --failure latency --duration 30s --latency 5000ms
        chaos attack --service web --failure kill --auto-restart
        chaos attack --service auth --failure database-drop --duration 60s
    """
    rprint(Panel.fit(
        f"[bold red]🐒 ChaosMonkey-Lite v1.0.0[/bold red]\n\n"
        f"[yellow]⚠️  Starting chaos attack[/yellow]\n"
        f"[cyan]🎯 Target: {service}[/cyan]\n"
        f"[red]💥 Attack: {failure}[/red]\n"
        f"[blue]⏱️  Duration: {duration}[/blue]",
        title="Chaos Attack"
    ))
    
    # Parse duration
    duration_seconds = _parse_duration(duration)
    
    # Initialize safety guards
    safety = SafetyGuards()
    
    if not force:
        console.print("[yellow]🔍 Running pre-flight checks...[/yellow]")
        if not safety.pre_flight_check(service):
            console.print("[red]❌ Pre-flight checks failed. Aborting attack.[/red]")
            return
        console.print("[green]✅ Pre-flight checks passed[/green]")
    
    # Initialize metrics collector
    metrics = MetricsCollector(service)
    
    # Collect baseline metrics
    console.print("[yellow]📊 Collecting baseline metrics...[/yellow]")
    baseline = metrics.collect_baseline()
    _display_metrics(baseline, "Baseline Metrics")
    
    # Execute attack based on type
    attack_instance = None
    try:
        if failure == 'latency':
            latency_ms = _parse_latency(latency)
            attack_instance = LatencyAttack(service, latency_ms, duration_seconds)
        elif failure == 'kill':
            attack_instance = ContainerKillAttack(service, auto_restart)
        elif failure == 'database-drop':
            attack_instance = DatabaseDropAttack(service, duration_seconds)
        elif failure == 'network-partition':
            if not target:
                console.print("[red]❌ --target required for network-partition[/red]")
                return
            attack_instance = NetworkPartitionAttack(service, target, duration_seconds)
        
        console.print(f"[red]🔥 Injecting {failure} failure...[/red]")
        
        # Execute attack
        attack_instance.execute()
        
        # Monitor during attack
        console.print("[yellow]⏳ Monitoring system response...[/yellow]")
        attack_metrics = metrics.monitor_during_attack(duration_seconds, attack_instance)
        
        # Rollback
        console.print("[yellow]🔄 Rolling back changes...[/yellow]")
        attack_instance.rollback()
        
        # Measure recovery
        console.print("[yellow]⏱️  Measuring recovery time...[/yellow]")
        recovery_time = metrics.measure_recovery_time()
        
        # Collect final metrics
        final_metrics = metrics.collect_final()
        
        # Display results
        _display_attack_results(baseline, attack_metrics, final_metrics, recovery_time, failure)
        
        # Save experiment
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        _save_experiment(experiment_id, service, failure, duration, baseline, attack_metrics, final_metrics, recovery_time)
        
        console.print(f"[green]✅ Experiment completed: {experiment_id}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Attack failed: {str(e)}[/red]")
        if attack_instance:
            try:
                attack_instance.rollback()
                console.print("[yellow]🔄 Emergency rollback executed[/yellow]")
            except:
                pass


@cli.command()
@click.option('--config', required=True, help='Path to experiment configuration file')
def experiment(config):
    """
    Run a full chaos experiment from configuration file
    
    Example:
        chaos experiment --config experiments/configs/api-latency.yaml
    """
    rprint(Panel.fit(
        f"[bold blue]🧪 Experiment Mode[/bold blue]\n\n"
        f"[cyan]📁 Config: {config}[/cyan]",
        title="Chaos Experiment"
    ))
    
    try:
        with open(config, 'r') as f:
            if config.endswith('.yaml') or config.endswith('.yml'):
                exp_config = yaml.safe_load(f)
            else:
                exp_config = json.load(f)
        
        manager = ExperimentManager(exp_config)
        results = manager.run_experiment()
        
        _display_experiment_results(results)
        
    except FileNotFoundError:
        console.print(f"[red]❌ Config file not found: {config}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Experiment failed: {str(e)}[/red]")


@cli.command('experiment list')
def experiment_list():
    """List available experiment configurations"""
    console.print("[yellow]📋 Available Experiments:[/yellow]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Experiment", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Service", style="green")
    table.add_column("Type", style="yellow")
    
    experiments = [
        ("api-latency", "Inject latency into API service", "api", "latency"),
        ("web-kill", "Kill web service container", "web", "kill"),
        ("auth-db-drop", "Drop auth database connections", "auth", "database-drop"),
        ("network-partition", "Partition network between services", "gateway", "network-partition"),
    ]
    
    for exp in experiments:
        table.add_row(*exp)
    
    console.print(table)


@cli.command()
def status():
    """Display current system health status"""
    rprint(Panel.fit("[bold green]📊 System Health Status[/bold green]", title="Status"))
    
    metrics = MetricsCollector()
    
    config = Config()
    services = list(config.get('services', {}).keys())
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Latency", style="yellow")
    table.add_column("Availability", style="blue")
    
    for service in services:
        try:
            health = metrics.check_service_health(service)
            table.add_row(
                f"{service}",
                health['status'],
                f"{health['latency']}ms",
                f"{health['availability']}%"
            )
        except:
            table.add_row(
                f"{service}",
                "[red]UNKNOWN[/red]",
                "N/A",
                "N/A"
            )
    
    console.print(table)


@cli.command()
@click.option('--id', help='Experiment ID to view results')
def history(id=None):
    """View chaos experiment history"""
    if id:
        # View specific experiment
        try:
            with open(f'experiments/results/{id}.json', 'r') as f:
                results = json.load(f)
            _display_experiment_results(results)
        except FileNotFoundError:
            console.print(f"[red]❌ Experiment not found: {id}[/red]")
    else:
        # List all experiments
        console.print("[yellow]📜 Experiment History:[/yellow]")
        # Implementation would list all experiment files


@cli.command()
@click.option('--id', required=True, help='Experiment ID')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json', help='Output format')
def report(id, format):
    """Generate a detailed report for an experiment"""
    try:
        with open(f'experiments/results/{id}.json', 'r') as f:
            results = json.load(f)
        
        if format == 'json':
            console.print(json.dumps(results, indent=2))
        else:
            console.print(yaml.dump(results, default_flow_style=False))
            
    except FileNotFoundError:
        console.print(f"[red]❌ Experiment not found: {id}[/red]")


def _parse_duration(duration_str):
    """Parse duration string to seconds"""
    if duration_str.endswith('s'):
        return int(duration_str[:-1])
    elif duration_str.endswith('m'):
        return int(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        return int(duration_str[:-1]) * 3600
    return int(duration_str)


def _parse_latency(latency_str):
    """Parse latency string to milliseconds"""
    if latency_str.endswith('ms'):
        return int(latency_str[:-2])
    elif latency_str.endswith('s'):
        return int(latency_str[:-1]) * 1000
    return int(latency_str)


def _display_metrics(metrics, title):
    """Display metrics in a table"""
    table = Table(show_header=True, header_style="bold magenta", title=title)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in metrics.items():
        table.add_row(key, str(value))
    
    console.print(table)


def _display_attack_results(baseline, attack_metrics, final_metrics, recovery_time, failure_type):
    """Display attack results"""
    rprint(Panel.fit(
        f"[bold green]📊 Attack Results[/bold green]\n\n"
        f"[cyan]Failure Type:[/cyan] {failure_type}\n"
        f"[yellow]Recovery Time:[/yellow] {recovery_time}s\n"
        f"[blue]Availability Impact:[/blue] {final_metrics.get('availability', 0) - baseline.get('availability', 0):.2f}%\n"
        f"[red]Errors During Attack:[/red] {attack_metrics.get('error_count', 0)}\n"
        f"[green]System Health:[/green] {final_metrics.get('status', 'UNKNOWN')}",
        title="Results"
    ))


def _display_experiment_results(results):
    """Display experiment results"""
    rprint(Panel.fit(
        f"[bold blue]🧪 Experiment Results[/bold blue]\n\n"
        f"[cyan]Experiment ID:[/cyan] {results.get('id', 'N/A')}\n"
        f"[yellow]Status:[/yellow] {results.get('status', 'UNKNOWN')}\n"
        f"[green]Duration:[/green] {results.get('duration', 'N/A')}\n"
        f"[blue]Recovery Time:[/blue] {results.get('recovery_time', 'N/A')}s",
        title="Experiment"
    ))


def _save_experiment(experiment_id, service, failure, duration, baseline, attack_metrics, final_metrics, recovery_time):
    """Save experiment results to file"""
    import os
    os.makedirs('experiments/results', exist_ok=True)
    
    results = {
        'id': experiment_id,
        'timestamp': datetime.now().isoformat(),
        'service': service,
        'failure_type': failure,
        'duration': duration,
        'baseline_metrics': baseline,
        'attack_metrics': attack_metrics,
        'final_metrics': final_metrics,
        'recovery_time': recovery_time,
        'status': 'completed'
    }
    
    with open(f'experiments/results/{experiment_id}.json', 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == '__main__':
    cli()
