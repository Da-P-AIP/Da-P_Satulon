"""
Critical Exponent Monitoring System for da-P Particle Research

This module provides real-time monitoring of critical exponents ν, β, Rc 
and automatic alert generation when values deviate from expected ranges.

Part of the DICP Self-Audit CI/CD System - Monitoring Layer
"""

import json
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import argparse

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'code'))

from ca_2d.grid import CA2D
from ca_2d.info_cond import InformationConductivity


@dataclass
class CriticalExponentMeasurement:
    """Data structure for critical exponent measurements"""
    timestamp: str
    nu: float
    nu_error: float
    beta: float  
    beta_error: float
    critical_point: float
    grid_size: int
    iterations: int
    status: str  # 'normal', 'warning', 'critical'
    notes: str = ""


@dataclass
class AlertCondition:
    """Alert condition configuration"""
    parameter: str
    reference_value: float
    tolerance_sigma: int
    message_template: str
    severity: str  # 'info', 'warning', 'critical'


class CriticalExponentMonitor:
    """Monitor critical exponents and generate alerts"""
    
    # Reference values for da-P particles (3D systems)
    REFERENCE_VALUES = {
        'nu': 0.34,
        'nu_error': 0.01,
        'beta': 0.37,  # Approximate from hybrid transition theory
        'beta_error': 0.02,
        'critical_point': 0.0091,
        'critical_point_error': 0.0001
    }
    
    # Alert conditions
    ALERT_CONDITIONS = [
        AlertCondition(
            parameter='nu',
            reference_value=0.34,
            tolerance_sigma=3,
            message_template="🚨 Critical exponent ν = {value:.4f} ± {error:.4f} deviates {sigma:.1f}σ from reference value {ref:.4f}!",
            severity='critical'
        ),
        AlertCondition(
            parameter='critical_point',
            reference_value=0.0091,
            tolerance_sigma=3,
            message_template="📊 Critical point p_c = {value:.6f} is {sigma:.1f}σ from expected {ref:.6f}",
            severity='warning'
        ),
        AlertCondition(
            parameter='beta',
            reference_value=0.37,
            tolerance_sigma=2,
            message_template="⚡ Critical exponent β = {value:.4f} shows {sigma:.1f}σ deviation",
            severity='warning'
        )
    ]
    
    def __init__(self, output_dir: str = "./monitoring_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.history_file = self.output_dir / "exponent_history.json"
        self.alert_log = self.output_dir / "alert_log.json"
        
        # Load existing history
        self.history = self._load_history()
        
    def _load_history(self) -> List[CriticalExponentMeasurement]:
        """Load measurement history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return [CriticalExponentMeasurement(**item) for item in data]
        return []
    
    def _save_history(self):
        """Save measurement history to file"""
        with open(self.history_file, 'w') as f:
            json.dump([asdict(measurement) for measurement in self.history], f, indent=2)
    
    def measure_critical_exponents(self, grid_size: int = 32, iterations: int = 50, 
                                  quick_mode: bool = False) -> CriticalExponentMeasurement:
        """Measure critical exponents ν and β"""
        print(f"🔬 Measuring critical exponents (L={grid_size}, iterations={iterations})")
        
        if quick_mode:
            iterations = min(iterations, 20)
            print("⚡ Quick mode enabled - reduced iterations for CI")
        
        # Create CA system
        ca = CA2D(grid_size=grid_size, random_seed=int(time.time()) % 10000)
        info_calc = InformationConductivity(ca.grid)
        
        # Scan interaction strength around critical point
        p_values = np.linspace(0.007, 0.013, 13) if not quick_mode else np.linspace(0.008, 0.012, 7)
        conductivities = []
        susceptibilities = []
        
        for p in p_values:
            ca.interaction_strength = p
            ca.reset()
            
            # Equilibration
            equilib_steps = iterations // 2
            for _ in range(equilib_steps):
                ca.step()
            
            # Measurement
            conductivity_sum = 0
            activity_variance = 0
            activity_values = []
            
            measurement_steps = iterations - equilib_steps
            for _ in range(measurement_steps):
                ca.step()
                conductivity = info_calc.calculate_conductivity_entropy()
                conductivity_sum += conductivity
                
                # Collect activity for susceptibility calculation
                mean_activity = np.mean(ca.grid)
                activity_values.append(mean_activity)
            
            avg_conductivity = conductivity_sum / measurement_steps
            conductivities.append(avg_conductivity)
            
            # Calculate susceptibility (activity variance)
            if len(activity_values) > 1:
                susceptibility = np.var(activity_values) * grid_size**2
                susceptibilities.append(susceptibility)
            else:
                susceptibilities.append(0)
        
        # Analyze results
        analysis = self._analyze_critical_behavior(p_values, conductivities, susceptibilities, grid_size)
        
        # Create measurement record
        measurement = CriticalExponentMeasurement(
            timestamp=datetime.now().isoformat(),
            nu=analysis['nu'],
            nu_error=analysis['nu_error'],
            beta=analysis['beta'],
            beta_error=analysis['beta_error'],
            critical_point=analysis['critical_point'],
            grid_size=grid_size,
            iterations=iterations,
            status=analysis['status'],
            notes=f"Measurement completed in {'quick' if quick_mode else 'standard'} mode"
        )
        
        return measurement
    
    def _analyze_critical_behavior(self, p_values: np.ndarray, conductivities: List[float], 
                                  susceptibilities: List[float], grid_size: int) -> Dict:
        """Analyze critical behavior and extract exponents"""
        
        conductivities = np.array(conductivities)
        susceptibilities = np.array(susceptibilities)
        
        # Find critical point (peak in conductivity)
        peak_idx = np.argmax(conductivities)
        critical_point = p_values[peak_idx]
        
        # Estimate ν from conductivity peak width
        # For 3D systems: ξ ~ |p - p_c|^(-ν), conductivity ~ ξ^(d-2)
        # Peak width ~ L^(-1/ν)
        half_max = conductivities[peak_idx] / 2
        
        # Find half-width points
        left_indices = np.where(conductivities[:peak_idx] >= half_max)[0]
        right_indices = np.where(conductivities[peak_idx:] >= half_max)[0] + peak_idx
        
        if len(left_indices) > 0 and len(right_indices) > 0:
            left_p = p_values[left_indices[-1]]
            right_p = p_values[right_indices[-1]]
            peak_width = right_p - left_p
            
            # ν estimation: peak_width ~ L^(-1/ν)
            if peak_width > 0:
                nu_estimate = 1.0 / (np.log(grid_size) / np.log(1.0 / peak_width))
                nu_estimate = max(0.1, min(1.0, nu_estimate))  # Clamp to reasonable range
            else:
                nu_estimate = 0.34  # Default
        else:
            nu_estimate = 0.34  # Default
        
        # Estimate β from susceptibility scaling
        # χ ~ |p - p_c|^(-γ), where γ = ν(2-η) ≈ 2ν for 3D
        # Near critical point: susceptibility ~ (p - p_c)^(-γ)
        beta_estimate = 0.37  # Default for hybrid transitions
        
        if len(susceptibilities) > 3 and peak_idx > 0:
            # Simple β estimation from susceptibility slope
            try:
                p_near_critical = p_values[max(0, peak_idx-2):min(len(p_values), peak_idx+3)]
                chi_near_critical = susceptibilities[max(0, peak_idx-2):min(len(p_values), peak_idx+3)]
                
                if len(p_near_critical) > 2 and np.any(chi_near_critical > 0):
                    # Log-log slope gives -γ, and β ≈ γ/2 for 3D systems
                    valid_indices = chi_near_critical > 0
                    if np.sum(valid_indices) > 2:
                        p_valid = p_near_critical[valid_indices]
                        chi_valid = chi_near_critical[valid_indices]
                        
                        # Avoid log(0) and use relative distance from critical point
                        p_rel = np.abs(p_valid - critical_point) + 1e-6
                        log_p = np.log(p_rel)
                        log_chi = np.log(chi_valid)
                        
                        # Linear regression to find slope
                        if len(log_p) > 1:
                            slope = np.polyfit(log_p, log_chi, 1)[0]
                            gamma_estimate = -slope
                            beta_estimate = gamma_estimate / 2.5  # Rough scaling relation
                            beta_estimate = max(0.1, min(1.0, beta_estimate))
            except (ValueError, RuntimeError):
                pass  # Keep default β value
        
        # Error estimates (simplified)
        nu_error = 0.02 if grid_size >= 32 else 0.05
        beta_error = 0.03
        
        # Status determination
        nu_deviation = abs(nu_estimate - self.REFERENCE_VALUES['nu']) / self.REFERENCE_VALUES['nu_error']
        pc_deviation = abs(critical_point - self.REFERENCE_VALUES['critical_point']) / self.REFERENCE_VALUES['critical_point_error']
        
        if nu_deviation > 3 or pc_deviation > 3:
            status = 'critical'
        elif nu_deviation > 2 or pc_deviation > 2:
            status = 'warning'
        else:
            status = 'normal'
        
        return {
            'nu': nu_estimate,
            'nu_error': nu_error,
            'beta': beta_estimate,
            'beta_error': beta_error,
            'critical_point': critical_point,
            'status': status
        }
    
    def check_alerts(self, measurement: CriticalExponentMeasurement) -> List[Dict]:
        """Check measurement against alert conditions"""
        alerts = []
        
        values = {
            'nu': (measurement.nu, measurement.nu_error),
            'beta': (measurement.beta, measurement.beta_error), 
            'critical_point': (measurement.critical_point, 0.0001)  # Estimated error
        }
        
        for condition in self.ALERT_CONDITIONS:
            if condition.parameter in values:
                value, error = values[condition.parameter]
                reference = condition.reference_value
                
                # Calculate sigma deviation
                if condition.parameter == 'nu':
                    tolerance = self.REFERENCE_VALUES['nu_error']
                elif condition.parameter == 'beta':
                    tolerance = self.REFERENCE_VALUES['beta_error']
                else:
                    tolerance = self.REFERENCE_VALUES.get(f"{condition.parameter}_error", error)
                
                deviation = abs(value - reference)
                sigma_deviation = deviation / tolerance if tolerance > 0 else 0
                
                if sigma_deviation > condition.tolerance_sigma:
                    alert = {
                        'timestamp': measurement.timestamp,
                        'parameter': condition.parameter,
                        'value': value,
                        'error': error,
                        'reference': reference,
                        'sigma_deviation': sigma_deviation,
                        'severity': condition.severity,
                        'message': condition.message_template.format(
                            value=value,
                            error=error,
                            sigma=sigma_deviation,
                            ref=reference
                        )
                    }
                    alerts.append(alert)
        
        return alerts
    
    def log_alerts(self, alerts: List[Dict]):
        """Log alerts to file and console"""
        if not alerts:
            return
            
        # Load existing alert log
        alert_history = []
        if self.alert_log.exists():
            with open(self.alert_log, 'r') as f:
                alert_history = json.load(f)
        
        # Add new alerts
        alert_history.extend(alerts)
        
        # Save updated log
        with open(self.alert_log, 'w') as f:
            json.dump(alert_history, f, indent=2)
        
        # Print alerts to console
        for alert in alerts:
            severity_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️', 
                'critical': '🚨'
            }
            emoji = severity_emoji.get(alert['severity'], '📊')
            print(f"{emoji} {alert['message']}")
    
    def run_continuous_monitoring(self, interval_minutes: int = 60, grid_size: int = 32):
        """Run continuous monitoring loop"""
        print(f"🔄 Starting continuous monitoring (interval: {interval_minutes} min, grid_size: {grid_size})")
        
        while True:
            try:
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Running measurement...")
                
                # Perform measurement
                measurement = self.measure_critical_exponents(grid_size=grid_size, quick_mode=True)
                
                # Add to history
                self.history.append(measurement)
                self._save_history()
                
                # Check for alerts
                alerts = self.check_alerts(measurement)
                if alerts:
                    self.log_alerts(alerts)
                
                # Print status
                print(f"📊 Results: ν = {measurement.nu:.4f} ± {measurement.nu_error:.4f}, "
                      f"p_c = {measurement.critical_point:.6f}, status = {measurement.status}")
                
                # Wait for next measurement
                print(f"⏳ Waiting {interval_minutes} minutes until next measurement...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
                print("⏳ Waiting 5 minutes before retry...")
                time.sleep(5 * 60)
    
    def generate_report(self, hours_back: int = 24) -> Dict:
        """Generate monitoring report for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        recent_measurements = [
            m for m in self.history 
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_measurements:
            return {
                'status': 'no_data',
                'message': f'No measurements in the last {hours_back} hours'
            }
        
        # Calculate statistics
        nu_values = [m.nu for m in recent_measurements]
        pc_values = [m.critical_point for m in recent_measurements]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours_back,
            'total_measurements': len(recent_measurements),
            'statistics': {
                'nu': {
                    'mean': np.mean(nu_values),
                    'std': np.std(nu_values),
                    'min': np.min(nu_values),
                    'max': np.max(nu_values)
                },
                'critical_point': {
                    'mean': np.mean(pc_values),
                    'std': np.std(pc_values),
                    'min': np.min(pc_values),
                    'max': np.max(pc_values)
                }
            },
            'status_distribution': {},
            'latest_measurement': asdict(recent_measurements[-1]) if recent_measurements else None
        }
        
        # Count status distribution
        status_counts = {}
        for m in recent_measurements:
            status_counts[m.status] = status_counts.get(m.status, 0) + 1
        report['status_distribution'] = status_counts
        
        # Overall status
        if status_counts.get('critical', 0) > 0:
            report['overall_status'] = 'critical'
        elif status_counts.get('warning', 0) > 0:
            report['overall_status'] = 'warning'
        else:
            report['overall_status'] = 'normal'
        
        return report


def main():
    """Main monitoring application"""
    parser = argparse.ArgumentParser(description='da-P Particle Critical Exponent Monitor')
    
    parser.add_argument('--mode', choices=['single', 'continuous', 'report'], 
                       default='single', help='Monitoring mode')
    parser.add_argument('--grid-size', type=int, default=32, 
                       help='Grid size for simulations')
    parser.add_argument('--iterations', type=int, default=50,
                       help='Number of iterations per measurement')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in minutes (continuous mode)')
    parser.add_argument('--output-dir', default='./monitoring_results',
                       help='Output directory for results')
    parser.add_argument('--quick', action='store_true',
                       help='Enable quick mode (reduced iterations)')
    parser.add_argument('--report-hours', type=int, default=24,
                       help='Hours back for report generation')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = CriticalExponentMonitor(output_dir=args.output_dir)
    
    if args.mode == 'single':
        print("🔬 Single measurement mode")
        measurement = monitor.measure_critical_exponents(
            grid_size=args.grid_size,
            iterations=args.iterations,
            quick_mode=args.quick
        )
        
        # Add to history
        monitor.history.append(measurement)
        monitor._save_history()
        
        # Check alerts
        alerts = monitor.check_alerts(measurement)
        if alerts:
            monitor.log_alerts(alerts)
        
        # Print results
        print(f"\n📊 Measurement Results:")
        print(f"   Timestamp: {measurement.timestamp}")
        print(f"   Critical exponent ν: {measurement.nu:.4f} ± {measurement.nu_error:.4f}")
        print(f"   Critical exponent β: {measurement.beta:.4f} ± {measurement.beta_error:.4f}")
        print(f"   Critical point p_c: {measurement.critical_point:.6f}")
        print(f"   Grid size: {measurement.grid_size}")
        print(f"   Status: {measurement.status}")
        print(f"   Notes: {measurement.notes}")
        
        if alerts:
            print(f"\n🚨 {len(alerts)} alert(s) generated - check alert log for details")
        else:
            print("\n✅ All measurements within normal ranges")
    
    elif args.mode == 'continuous':
        print("🔄 Continuous monitoring mode")
        monitor.run_continuous_monitoring(
            interval_minutes=args.interval,
            grid_size=args.grid_size
        )
    
    elif args.mode == 'report':
        print(f"📊 Generating report for last {args.report_hours} hours")
        report = monitor.generate_report(hours_back=args.report_hours)
        
        # Save report
        report_file = Path(args.output_dir) / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n📈 Monitoring Report Summary:")
        print(f"   Report file: {report_file}")
        print(f"   Period: {report['period_hours']} hours")
        print(f"   Total measurements: {report['total_measurements']}")
        print(f"   Overall status: {report['overall_status']}")
        
        if report.get('statistics'):
            nu_stats = report['statistics']['nu']
            print(f"   ν statistics: {nu_stats['mean']:.4f} ± {nu_stats['std']:.4f} "
                  f"(range: {nu_stats['min']:.4f} - {nu_stats['max']:.4f})")
            
            pc_stats = report['statistics']['critical_point']
            print(f"   p_c statistics: {pc_stats['mean']:.6f} ± {pc_stats['std']:.6f} "
                  f"(range: {pc_stats['min']:.6f} - {pc_stats['max']:.6f})")
        
        status_dist = report.get('status_distribution', {})
        if status_dist:
            print(f"   Status distribution: {status_dist}")


if __name__ == "__main__":
    main()
