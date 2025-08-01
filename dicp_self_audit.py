#!/usr/bin/env python3
"""
DICP Self-Audit System - Main Controller

Orchestrates the complete da-P particle theory validation pipeline:
- Theory layer validation (conservation laws, critical exponents)
- Simulation layer testing (quick sweeps, scaling checks)
- Analysis layer verification (statistical consistency)
- Real-time monitoring and alerting

This is the central command center for the "理論-CI/CD パイプライン"
"""

import sys
import os
import json
import time
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile
import threading
import signal

# Add monitoring directory to path
sys.path.insert(0, str(Path(__file__).parent / 'monitoring'))

try:
    from critical_exponent_monitor import CriticalExponentMonitor
    from notification_bot import NotificationBot
except ImportError:
    print("❌ Required monitoring modules not found. Run from repository root.")
    sys.exit(1)


class DICPSelfAuditSystem:
    """Main controller for da-P particle self-audit system"""
    
    def __init__(self, config_file: str = "audit_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # Initialize components
        self.monitor = CriticalExponentMonitor(
            output_dir=self.config['monitoring']['output_dir']
        )
        self.notification_bot = NotificationBot(
            config_file=self.config['notifications']['config_file']
        )
        
        # State tracking
        self.running = False
        self.last_audit_time = None
        self.audit_history = []
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> Dict:
        """Load system configuration"""
        default_config = {
            'theory_validation': {
                'enabled': True,
                'test_modules': [
                    'tests.test_theory_validation::TestConservationLaws',
                    'tests.test_theory_validation::TestCriticalExponents',
                    'tests.test_theory_validation::TestDimensionalAnalysis'
                ],
                'pytest_args': ['-v', '--tb=short']
            },
            'simulation_validation': {
                'enabled': True,
                'quick_sweep': {
                    'grid_size': 32,
                    'iterations': 20,
                    'interaction_steps': 5
                },
                'scaling_test': {
                    'grid_sizes': [16, 32],
                    'iterations': 30
                }
            },
            'monitoring': {
                'enabled': True,
                'output_dir': './monitoring_results',
                'measurement_interval_minutes': 60,
                'continuous_mode': False
            },
            'notifications': {
                'enabled': True,
                'config_file': 'notification_config.json'
            },
            'audit_schedule': {
                'theory_check_minutes': 30,
                'simulation_check_minutes': 120,
                'full_audit_hours': 24
            },
            'thresholds': {
                'nu_deviation_warning': 2.0,  # sigma
                'nu_deviation_critical': 3.0,  # sigma
                'critical_point_tolerance': 0.001
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                # Deep merge with defaults
                self._deep_merge(default_config, loaded_config)
                return loaded_config
        else:
            # Create default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📝 Created default config: {self.config_file}")
            return default_config
    
    def _deep_merge(self, base: Dict, update: Dict):
        """Deep merge configuration dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run_theory_validation(self) -> Dict:
        """Run complete theory validation test suite"""
        print("🔬 Running theory validation tests...")
        
        if not self.config['theory_validation']['enabled']:
            return {'status': 'skipped', 'reason': 'Theory validation disabled'}
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': [],
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Run pytest with specified modules
            test_modules = self.config['theory_validation']['test_modules']
            pytest_args = ['python', '-m', 'pytest'] + test_modules + self.config['theory_validation']['pytest_args']
            
            print(f"🧪 Running: {' '.join(pytest_args)}")
            
            result = subprocess.run(
                pytest_args,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            results['execution_time'] = time.time() - start_time
            results['return_code'] = result.returncode
            results['stdout'] = result.stdout
            results['stderr'] = result.stderr
            
            # Parse test results
            if result.returncode == 0:
                results['status'] = 'passed'
                # Count passed tests from output
                if 'passed' in result.stdout:
                    import re
                    match = re.search(r'(\d+) passed', result.stdout)
                    if match:
                        results['tests_passed'] = int(match.group(1))
            else:
                results['status'] = 'failed'
                # Extract failure information
                if 'FAILED' in result.stdout:
                    failures = []
                    for line in result.stdout.split('\n'):
                        if 'FAILED' in line:
                            failures.append(line.strip())
                    results['failures'] = failures
                    results['tests_failed'] = len(failures)
                
                # Send alert for theory breach
                if self.config['notifications']['enabled']:
                    self.notification_bot.send_theory_breach_alert(
                        'Theory Validation Suite',
                        f"Tests failed with return code {result.returncode}",
                        commit_sha=self._get_current_commit_sha()
                    )
        
        except subprocess.TimeoutExpired:
            results['status'] = 'timeout'
            results['execution_time'] = time.time() - start_time
            print("⏰ Theory validation tests timed out")
        
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
            results['execution_time'] = time.time() - start_time
            print(f"❌ Error running theory validation: {e}")
        
        print(f"🔬 Theory validation completed: {results['status']} ({results['execution_time']:.1f}s)")
        return results
    
    def run_simulation_validation(self) -> Dict:
        """Run simulation layer validation"""
        print("🖥️ Running simulation validation...")
        
        if not self.config['simulation_validation']['enabled']:
            return {'status': 'skipped', 'reason': 'Simulation validation disabled'}
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'quick_sweep': None,
            'scaling_test': None,
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Quick sweep test
            quick_config = self.config['simulation_validation']['quick_sweep']
            print(f"🚀 Running quick sweep (L={quick_config['grid_size']})")
            
            quick_result = self._run_quick_sweep(quick_config)
            results['quick_sweep'] = quick_result
            
            # Scaling test
            scaling_config = self.config['simulation_validation']['scaling_test']
            print(f"📏 Running scaling test (sizes: {scaling_config['grid_sizes']})")
            
            scaling_result = self._run_scaling_test(scaling_config)
            results['scaling_test'] = scaling_result
            
            # Overall status
            if (quick_result['status'] == 'passed' and scaling_result['status'] == 'passed'):
                results['status'] = 'passed'
            elif 'failed' in [quick_result['status'], scaling_result['status']]:
                results['status'] = 'failed'
            else:
                results['status'] = 'warning'
        
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
            print(f"❌ Error in simulation validation: {e}")
        
        results['execution_time'] = time.time() - start_time
        print(f"🖥️ Simulation validation completed: {results['status']} ({results['execution_time']:.1f}s)")
        
        return results
    
    def _run_quick_sweep(self, config: Dict) -> Dict:
        """Run quick simulation sweep"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                cmd = [
                    'python', 'run_experiments.py',
                    '--grid-size', str(config['grid_size']),
                    '--iterations', str(config['iterations']),
                    '--interaction-steps', str(config['interaction_steps']),
                    '--output-dir', temp_dir,
                    '--run-id', f'audit_quick_{int(time.time())}',
                    '--conductivity-method', 'entropy'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Validate results
                    results_files = list(Path(temp_dir).glob('*/results_summary.csv'))
                    if results_files:
                        import pandas as pd
                        df = pd.read_csv(results_files[0])
                        
                        # Basic sanity checks
                        max_conductivity = df['conductivity_entropy'].max()
                        critical_interaction = df.loc[df['conductivity_entropy'].idxmax(), 'interaction_strength']
                        
                        if 0.005 < critical_interaction < 0.015 and max_conductivity > 0:
                            return {
                                'status': 'passed',
                                'critical_point': float(critical_interaction),
                                'max_conductivity': float(max_conductivity),
                                'execution_time': result.args
                            }
                        else:
                            return {
                                'status': 'failed',
                                'reason': f'Critical point {critical_interaction:.6f} or conductivity {max_conductivity:.6f} out of range'
                            }
                    else:
                        return {'status': 'failed', 'reason': 'No results file generated'}
                else:
                    return {
                        'status': 'failed',
                        'reason': f'Simulation failed with return code {result.returncode}',
                        'stderr': result.stderr
                    }
            
            except subprocess.TimeoutExpired:
                return {'status': 'timeout', 'reason': 'Quick sweep timed out'}
            except Exception as e:
                return {'status': 'error', 'reason': str(e)}
    
    def _run_scaling_test(self, config: Dict) -> Dict:
        """Run scaling consistency test"""
        grid_sizes = config['grid_sizes']
        iterations = config['iterations']
        
        critical_points = []
        
        for size in grid_sizes:
            try:
                # Quick measurement for each size
                measurement = self.monitor.measure_critical_exponents(
                    grid_size=size, 
                    iterations=iterations, 
                    quick_mode=True
                )
                critical_points.append((size, measurement.critical_point))
                
            except Exception as e:
                return {
                    'status': 'error',
                    'reason': f'Failed to measure L={size}: {e}'
                }
        
        if len(critical_points) >= 2:
            # Check consistency between sizes
            pc_values = [pc for size, pc in critical_points]
            pc_std = np.std(pc_values) if len(pc_values) > 1 else 0
            pc_mean = np.mean(pc_values)
            
            # Tolerance based on expected finite-size effects
            tolerance = self.config['thresholds']['critical_point_tolerance']
            
            if pc_std < tolerance:
                return {
                    'status': 'passed',
                    'critical_points': critical_points,
                    'mean_pc': float(pc_mean),
                    'std_pc': float(pc_std)
                }
            else:
                return {
                    'status': 'warning',
                    'reason': f'Critical point scatter {pc_std:.6f} > tolerance {tolerance:.6f}',
                    'critical_points': critical_points,
                    'mean_pc': float(pc_mean),
                    'std_pc': float(pc_std)
                }
        else:
            return {'status': 'failed', 'reason': 'Insufficient measurements for scaling test'}
    
    def run_critical_exponent_measurement(self) -> Dict:
        """Run critical exponent measurement and check for alerts"""
        print("📊 Running critical exponent measurement...")
        
        if not self.config['monitoring']['enabled']:
            return {'status': 'skipped', 'reason': 'Monitoring disabled'}
        
        try:
            # Perform measurement
            measurement = self.monitor.measure_critical_exponents(
                grid_size=32,  # Standard monitoring size
                iterations=50,
                quick_mode=False
            )
            
            # Check for alerts
            alerts = self.monitor.check_alerts(measurement)
            
            # Send notifications if alerts found
            if alerts and self.config['notifications']['enabled']:
                for alert in alerts:
                    if alert['parameter'] == 'nu':
                        self.notification_bot.send_critical_exponent_alert(
                            'nu',
                            alert['value'],
                            alert['reference'],
                            alert['sigma_deviation']
                        )
                    elif alert['parameter'] == 'critical_point':
                        self.notification_bot.send_critical_exponent_alert(
                            'critical_point',
                            alert['value'],
                            alert['reference'],
                            alert['sigma_deviation']
                        )
            
            # Add to monitor history
            self.monitor.history.append(measurement)
            self.monitor._save_history()
            
            result = {
                'status': measurement.status,
                'measurement': {
                    'nu': measurement.nu,
                    'nu_error': measurement.nu_error,
                    'beta': measurement.beta,
                    'beta_error': measurement.beta_error,
                    'critical_point': measurement.critical_point,
                    'grid_size': measurement.grid_size
                },
                'alerts_count': len(alerts),
                'timestamp': measurement.timestamp
            }
            
            print(f"📊 Critical exponent measurement: ν = {measurement.nu:.4f} ± {measurement.nu_error:.4f}, status = {measurement.status}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in critical exponent measurement: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_full_audit(self) -> Dict:
        """Run complete system audit"""
        print("🔍 Running full system audit...")
        
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'audit_id': f'audit_{int(time.time())}',
            'overall_status': 'unknown',
            'theory_validation': None,
            'simulation_validation': None,
            'critical_exponent_measurement': None,
            'total_execution_time': 0
        }
        
        start_time = time.time()
        
        # Theory validation
        theory_results = self.run_theory_validation()
        audit_results['theory_validation'] = theory_results
        
        # Simulation validation
        simulation_results = self.run_simulation_validation()
        audit_results['simulation_validation'] = simulation_results
        
        # Critical exponent measurement
        measurement_results = self.run_critical_exponent_measurement()
        audit_results['critical_exponent_measurement'] = measurement_results
        
        audit_results['total_execution_time'] = time.time() - start_time
        
        # Determine overall status
        statuses = [
            theory_results.get('status'),
            simulation_results.get('status'),
            measurement_results.get('status')
        ]
        
        if any(s == 'failed' for s in statuses):
            audit_results['overall_status'] = 'failed'
        elif any(s == 'warning' for s in statuses):
            audit_results['overall_status'] = 'warning'
        elif all(s in ['passed', 'skipped'] for s in statuses):
            audit_results['overall_status'] = 'passed'
        else:
            audit_results['overall_status'] = 'unknown'
        
        # Save audit results
        self.audit_history.append(audit_results)
        self._save_audit_history()
        
        print(f"🔍 Full audit completed: {audit_results['overall_status']} ({audit_results['total_execution_time']:.1f}s)")
        
        # Send notification for critical failures
        if (audit_results['overall_status'] == 'failed' and 
            self.config['notifications']['enabled']):
            
            failed_components = []
            if theory_results.get('status') == 'failed':
                failed_components.append('Theory Validation')
            if simulation_results.get('status') == 'failed':
                failed_components.append('Simulation Validation')
            if measurement_results.get('status') == 'failed':
                failed_components.append('Critical Exponent Measurement')
            
            self.notification_bot.send_alert(
                'theory_breach',
                'System Audit Failure',
                f"Full system audit failed. Failed components: {', '.join(failed_components)}",
                {
                    'audit_id': audit_results['audit_id'],
                    'failed_components': failed_components,
                    'execution_time': audit_results['total_execution_time']
                },
                'critical'
            )
        
        return audit_results
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring mode"""
        print("🔄 Starting continuous monitoring mode...")
        self.running = True
        
        # Schedule trackers
        last_theory_check = datetime.now()
        last_simulation_check = datetime.now()
        last_full_audit = datetime.now()
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if it's time for theory validation
                if (current_time - last_theory_check).total_seconds() >= self.config['audit_schedule']['theory_check_minutes'] * 60:
                    print(f"\n⏰ Scheduled theory check at {current_time.strftime('%H:%M:%S')}")
                    self.run_theory_validation()
                    last_theory_check = current_time
                
                # Check if it's time for simulation validation
                if (current_time - last_simulation_check).total_seconds() >= self.config['audit_schedule']['simulation_check_minutes'] * 60:
                    print(f"\n⏰ Scheduled simulation check at {current_time.strftime('%H:%M:%S')}")
                    self.run_simulation_validation()
                    last_simulation_check = current_time
                
                # Check if it's time for full audit
                if (current_time - last_full_audit).total_seconds() >= self.config['audit_schedule']['full_audit_hours'] * 3600:
                    print(f"\n⏰ Scheduled full audit at {current_time.strftime('%H:%M:%S')}")
                    self.run_full_audit()
                    last_full_audit = current_time
                
                # Regular critical exponent measurement
                if self.config['monitoring']['continuous_mode']:
                    self.run_critical_exponent_measurement()
                
                # Sleep for a minute before next check
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Error in continuous monitoring: {e}")
                time.sleep(60)  # Wait before retrying
        
        print("🛑 Continuous monitoring stopped")
    
    def _save_audit_history(self):
        """Save audit history to file"""
        history_file = Path(self.config['monitoring']['output_dir']) / 'audit_history.json'
        history_file.parent.mkdir(exist_ok=True)
        
        with open(history_file, 'w') as f:
            json.dump(self.audit_history, f, indent=2)
    
    def _get_current_commit_sha(self) -> str:
        """Get current git commit SHA"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return 'unknown'
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_running': self.running,
            'last_audit_time': self.last_audit_time,
            'components': {
                'theory_validation': self.config['theory_validation']['enabled'],
                'simulation_validation': self.config['simulation_validation']['enabled'],
                'monitoring': self.config['monitoring']['enabled'],
                'notifications': self.config['notifications']['enabled']
            },
            'recent_measurements': len(self.monitor.history),
            'recent_audits': len(self.audit_history)
        }
        
        # Get latest measurement if available
        if self.monitor.history:
            latest = self.monitor.history[-1]
            status['latest_measurement'] = {
                'nu': latest.nu,
                'critical_point': latest.critical_point,
                'status': latest.status,
                'timestamp': latest.timestamp
            }
        
        return status


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='DICP Self-Audit System for da-P Particle Research',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full audit once
  python dicp_self_audit.py --mode full-audit
  
  # Run continuous monitoring
  python dicp_self_audit.py --mode continuous
  
  # Run only theory validation
  python dicp_self_audit.py --mode theory-only
  
  # Get system status
  python dicp_self_audit.py --mode status
        """
    )
    
    parser.add_argument('--mode', 
                       choices=['full-audit', 'continuous', 'theory-only', 'simulation-only', 'measurement-only', 'status'],
                       default='full-audit',
                       help='Operation mode')
    
    parser.add_argument('--config', default='audit_config.json',
                       help='Configuration file path')
    
    parser.add_argument('--output-dir', 
                       help='Override output directory for results')
    
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    # Initialize system
    audit_system = DICPSelfAuditSystem(config_file=args.config)
    
    # Override output directory if specified
    if args.output_dir:
        audit_system.config['monitoring']['output_dir'] = args.output_dir
        audit_system.monitor = CriticalExponentMonitor(output_dir=args.output_dir)
    
    # Execute based on mode
    if args.mode == 'full-audit':
        print("🚀 Running full system audit...")
        results = audit_system.run_full_audit()
        
        if not args.quiet:
            print(f"\n📊 Audit Results:")
            print(f"   Overall Status: {results['overall_status']}")
            print(f"   Execution Time: {results['total_execution_time']:.1f}s")
            print(f"   Theory: {results['theory_validation']['status']}")
            print(f"   Simulation: {results['simulation_validation']['status']}")
            print(f"   Measurement: {results['critical_exponent_measurement']['status']}")
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_status'] in ['passed', 'warning'] else 1)
    
    elif args.mode == 'continuous':
        print("🔄 Starting continuous monitoring...")
        audit_system.run_continuous_monitoring()
    
    elif args.mode == 'theory-only':
        results = audit_system.run_theory_validation()
        if not args.quiet:
            print(f"Theory validation: {results['status']}")
        sys.exit(0 if results['status'] in ['passed', 'skipped'] else 1)
    
    elif args.mode == 'simulation-only':
        results = audit_system.run_simulation_validation()
        if not args.quiet:
            print(f"Simulation validation: {results['status']}")
        sys.exit(0 if results['status'] in ['passed', 'skipped'] else 1)
    
    elif args.mode == 'measurement-only':
        results = audit_system.run_critical_exponent_measurement()
        if not args.quiet:
            print(f"Critical exponent measurement: {results['status']}")
        sys.exit(0 if results['status'] in ['normal', 'warning', 'skipped'] else 1)
    
    elif args.mode == 'status':
        status = audit_system.get_system_status()
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    # Add numpy import for scaling test
    import numpy as np
    main()
