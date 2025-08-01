"""
Discord/Slack Notification Bot for da-P Particle Research

Sends real-time alerts when critical exponents deviate from expected values
or when theory validation tests fail.

Part of the DICP Self-Audit CI/CD System - Alert Layer
"""

import json
import os
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import argparse
from pathlib import Path


class NotificationBot:
    """Handle Discord and Slack notifications for da-P particle research"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # Notification templates
        self.templates = {
            'theory_breach': {
                'title': '🚨 THEORY BREACH DETECTED',
                'color': 0xFF0000,  # Red
                'emoji': '🚨'
            },
            'critical_exponent_alert': {
                'title': '📊 Critical Exponent Alert',
                'color': 0xFF8800,  # Orange
                'emoji': '⚠️'
            },
            'simulation_failure': {
                'title': '💻 Simulation Failure',
                'color': 0xFFAA00,  # Yellow-Orange
                'emoji': '❌'
            },
            'nightly_report': {
                'title': '🌙 Nightly Validation Report',
                'color': 0x00AA88,  # Teal
                'emoji': '📈'
            },
            'success': {
                'title': '✅ All Systems Nominal',
                'color': 0x00FF00,  # Green
                'emoji': '✅'
            }
        }
    
    def _load_config(self) -> Dict:
        """Load notification configuration"""
        default_config = {
            'discord': {
                'enabled': False,
                'webhook_url': '',
                'channel_name': 'dicp-alerts'
            },
            'slack': {
                'enabled': False,
                'webhook_url': '',
                'channel': '#dicp-alerts'
            },
            'notifications': {
                'theory_breach': True,
                'critical_exponent_alert': True,
                'simulation_failure': True,
                'nightly_report': False,
                'success': False
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in loaded_config:
                        loaded_config[key] = default_config[key]
                return loaded_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📝 Created default config file: {self.config_file}")
            print("Please edit the config file to add your webhook URLs")
            return default_config
    
    def send_discord_message(self, message_type: str, title: str, description: str, 
                           fields: List[Dict] = None, footer: str = None) -> bool:
        """Send message to Discord via webhook"""
        if not self.config['discord']['enabled']:
            return False
            
        webhook_url = self.config['discord']['webhook_url']
        if not webhook_url:
            print("❌ Discord webhook URL not configured")
            return False
        
        template = self.templates.get(message_type, self.templates['critical_exponent_alert'])
        
        embed = {
            'title': title,
            'description': description,
            'color': template['color'],
            'timestamp': datetime.utcnow().isoformat(),
            'footer': {
                'text': footer or 'da-P Particle Research - DICP Self-Audit System'
            }
        }
        
        if fields:
            embed['fields'] = fields
        
        payload = {
            'embeds': [embed],
            'username': 'da-P Monitor',
            'avatar_url': 'https://raw.githubusercontent.com/Da-P-AIP/Da-P_Satulon/main/docs/dap_particle_icon.png'
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✅ Discord message sent successfully")
            return True
        except requests.RequestException as e:
            print(f"❌ Failed to send Discord message: {e}")
            return False
    
    def send_slack_message(self, message_type: str, title: str, description: str,
                          fields: List[Dict] = None, footer: str = None) -> bool:
        """Send message to Slack via webhook"""
        if not self.config['slack']['enabled']:
            return False
            
        webhook_url = self.config['slack']['webhook_url']
        if not webhook_url:
            print("❌ Slack webhook URL not configured")
            return False
        
        template = self.templates.get(message_type, self.templates['critical_exponent_alert'])
        
        # Build Slack message blocks
        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f"{template['emoji']} {title}"
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': description
                }
            }
        ]
        
        # Add fields as sections
        if fields:
            for field in fields:
                blocks.append({
                    'type': 'section',
                    'fields': [
                        {
                            'type': 'mrkdwn',
                            'text': f"*{field['name']}*\n{field['value']}"
                        }
                    ]
                })
        
        # Add footer
        blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': footer or 'da-P Particle Research - DICP Self-Audit System'
                }
            ]
        })
        
        payload = {
            'channel': self.config['slack']['channel'],
            'username': 'da-P Monitor',
            'icon_emoji': ':microscope:',
            'blocks': blocks
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✅ Slack message sent successfully")
            return True
        except requests.RequestException as e:
            print(f"❌ Failed to send Slack message: {e}")
            return False
    
    def send_alert(self, message_type: str, title: str, description: str,
                   details: Dict = None, priority: str = 'normal') -> bool:
        """Send alert to all configured channels"""
        
        # Check if this message type is enabled
        if not self.config['notifications'].get(message_type, True):
            print(f"📴 Notifications disabled for message type: {message_type}")
            return False
        
        # Build fields from details
        fields = []
        if details:
            for key, value in details.items():
                # Format the key nicely
                display_key = key.replace('_', ' ').title()
                
                # Format the value based on type
                if isinstance(value, float):
                    if 'exponent' in key.lower() or key.lower() in ['nu', 'beta']:
                        display_value = f"{value:.4f}"
                    elif 'critical_point' in key.lower():
                        display_value = f"{value:.6f}"
                    else:
                        display_value = f"{value:.3f}"
                elif isinstance(value, str) and value.count('-') == 2 and 'T' in value:
                    # ISO timestamp - make it readable
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        display_value = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except:
                        display_value = str(value)
                else:
                    display_value = str(value)
                
                fields.append({
                    'name': display_key,
                    'value': display_value,
                    'inline': True
                })
        
        # Add priority and timestamp
        fields.append({
            'name': 'Priority',
            'value': priority.upper(),
            'inline': True
        })
        
        fields.append({
            'name': 'Timestamp',
            'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'inline': True
        })
        
        success = True
        
        # Send to Discord
        if self.config['discord']['enabled']:
            discord_success = self.send_discord_message(
                message_type, title, description, fields
            )
            success = success and discord_success
        
        # Send to Slack
        if self.config['slack']['enabled']:
            slack_success = self.send_slack_message(
                message_type, title, description, fields
            )
            success = success and slack_success
        
        return success
    
    def send_theory_breach_alert(self, test_name: str, error_message: str, 
                               commit_sha: str = None, run_id: str = None):
        """Send critical theory breach alert"""
        title = "🚨 THEORY VALIDATION FAILURE"
        description = f"Critical theory test **{test_name}** has failed!\n\n**Error:** {error_message}"
        
        details = {
            'test_name': test_name,
            'error_type': 'Theory Breach',
            'commit_sha': commit_sha or 'unknown',
            'run_id': run_id or 'unknown'
        }
        
        return self.send_alert('theory_breach', title, description, details, 'critical')
    
    def send_critical_exponent_alert(self, parameter: str, measured_value: float, 
                                   expected_value: float, sigma_deviation: float,
                                   grid_size: int = None):
        """Send critical exponent deviation alert"""
        title = f"📊 Critical Exponent Alert: {parameter.upper()}"
        description = f"Critical exponent **{parameter}** = {measured_value:.4f} deviates {sigma_deviation:.1f}σ from expected value {expected_value:.4f}"
        
        if sigma_deviation >= 3:
            description += "\n\n⚠️ **This is a significant deviation requiring immediate investigation!**"
        
        details = {
            'parameter': parameter,
            'measured_value': measured_value,
            'expected_value': expected_value,
            'sigma_deviation': sigma_deviation,
            'grid_size': grid_size or 'unknown'
        }
        
        priority = 'critical' if sigma_deviation >= 3 else 'warning'
        return self.send_alert('critical_exponent_alert', title, description, details, priority)
    
    def send_simulation_failure_alert(self, simulation_type: str, error_message: str,
                                    grid_size: int = None, iterations: int = None):
        """Send simulation failure alert"""
        title = f"💻 Simulation Failure: {simulation_type}"
        description = f"Simulation **{simulation_type}** failed with error:\n\n```{error_message}```"
        
        details = {
            'simulation_type': simulation_type,
            'grid_size': grid_size,
            'iterations': iterations,
            'error_type': 'Simulation Failure'
        }
        
        return self.send_alert('simulation_failure', title, description, details, 'warning')
    
    def send_nightly_report(self, report_data: Dict):
        """Send nightly validation report"""
        title = "🌙 Nightly Validation Report"
        
        status = report_data.get('overall_status', 'unknown')
        total_measurements = report_data.get('total_measurements', 0)
        
        if status == 'critical':
            description = f"**❌ CRITICAL ISSUES DETECTED**\n\nNightly validation found {total_measurements} measurements with critical deviations."
        elif status == 'warning':
            description = f"**⚠️ Warnings detected**\n\nNightly validation completed with {total_measurements} measurements. Some parameters show minor deviations."
        else:
            description = f"**✅ All systems nominal**\n\nNightly validation completed successfully with {total_measurements} measurements."
        
        # Add statistics if available
        if 'statistics' in report_data:
            stats = report_data['statistics']
            if 'nu' in stats:
                nu_stats = stats['nu']
                description += f"\n\n**ν statistics:** {nu_stats['mean']:.4f} ± {nu_stats['std']:.4f}"
            
            if 'critical_point' in stats:
                pc_stats = stats['critical_point']
                description += f"\n**p_c statistics:** {pc_stats['mean']:.6f} ± {pc_stats['std']:.6f}"
        
        details = {
            'overall_status': status,
            'total_measurements': total_measurements,
            'period_hours': report_data.get('period_hours', 24)
        }
        
        # Add status distribution
        if 'status_distribution' in report_data:
            status_dist = report_data['status_distribution']
            for status_type, count in status_dist.items():
                details[f'{status_type}_count'] = count
        
        priority = 'critical' if status == 'critical' else 'normal'
        return self.send_alert('nightly_report', title, description, details, priority)
    
    def send_success_notification(self, message: str, details: Dict = None):
        """Send success notification"""
        title = "✅ Success"
        description = message
        
        return self.send_alert('success', title, description, details, 'normal')
    
    def test_notifications(self):
        """Test all configured notification channels"""
        print("🧪 Testing notification channels...")
        
        test_details = {
            'test_parameter': 'nu',
            'test_value': 0.342,
            'expected_value': 0.340,
            'sigma_deviation': 0.2,
            'grid_size': 32
        }
        
        success = self.send_alert(
            'critical_exponent_alert',
            '🧪 Test Notification',
            'This is a test message to verify notification channels are working correctly.',
            test_details,
            'normal'
        )
        
        if success:
            print("✅ Test notifications sent successfully!")
        else:
            print("❌ Some test notifications failed - check configuration")
        
        return success


def main():
    """Main notification bot application"""
    parser = argparse.ArgumentParser(description='da-P Particle Notification Bot')
    
    parser.add_argument('--config', default='notification_config.json',
                       help='Path to notification configuration file')
    parser.add_argument('--test', action='store_true',
                       help='Send test notifications')
    parser.add_argument('--monitor-file', 
                       help='Monitor alert log file for new alerts')
    parser.add_argument('--check-interval', type=int, default=60,
                       help='Check interval in seconds for file monitoring')
    
    # Alert sending options
    parser.add_argument('--send-alert', choices=['theory', 'exponent', 'simulation', 'report'],
                       help='Send specific alert type')
    parser.add_argument('--title', help='Alert title')
    parser.add_argument('--message', help='Alert message')
    parser.add_argument('--details', help='Alert details as JSON string')
    
    args = parser.parse_args()
    
    # Create notification bot
    bot = NotificationBot(config_file=args.config)
    
    if args.test:
        print("🧪 Running notification test...")
        bot.test_notifications()
        return
    
    if args.send_alert:
        if not args.title or not args.message:
            print("❌ --title and --message are required for sending alerts")
            return
        
        details = {}
        if args.details:
            try:
                details = json.loads(args.details)
            except json.JSONDecodeError:
                print("❌ Invalid JSON in --details")
                return
        
        if args.send_alert == 'theory':
            bot.send_theory_breach_alert(
                args.title, args.message,
                commit_sha=details.get('commit_sha'),
                run_id=details.get('run_id')
            )
        elif args.send_alert == 'exponent':
            bot.send_critical_exponent_alert(
                details.get('parameter', 'nu'),
                details.get('measured_value', 0.0),
                details.get('expected_value', 0.34),
                details.get('sigma_deviation', 0.0),
                details.get('grid_size')
            )
        elif args.send_alert == 'simulation':
            bot.send_simulation_failure_alert(
                args.title, args.message,
                details.get('grid_size'),
                details.get('iterations')
            )
        elif args.send_alert == 'report':
            bot.send_nightly_report(details)
        
        return
    
    if args.monitor_file:
        print(f"👁️ Monitoring alert file: {args.monitor_file}")
        monitor_alert_file(bot, args.monitor_file, args.check_interval)
        return
    
    print("💬 Notification bot ready. Use --help for usage options.")


def monitor_alert_file(bot: NotificationBot, alert_file: str, check_interval: int):
    """Monitor alert log file and send notifications for new alerts"""
    alert_path = Path(alert_file)
    last_size = 0
    
    if alert_path.exists():
        last_size = alert_path.stat().st_size
    
    print(f"👁️ Starting file monitoring (checking every {check_interval}s)")
    
    try:
        while True:
            time.sleep(check_interval)
            
            if not alert_path.exists():
                continue
            
            current_size = alert_path.stat().st_size
            if current_size <= last_size:
                continue
            
            # File has grown - check for new alerts
            try:
                with open(alert_path, 'r') as f:
                    alerts = json.load(f)
                
                # Find alerts newer than our last check
                cutoff_time = datetime.now().timestamp() - check_interval * 2
                
                for alert in alerts:
                    alert_time = datetime.fromisoformat(alert['timestamp']).timestamp()
                    if alert_time > cutoff_time:
                        # Send notification for this alert
                        send_alert_notification(bot, alert)
                
                last_size = current_size
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Error reading alert file: {e}")
            
    except KeyboardInterrupt:
        print("\n🛑 File monitoring stopped")


def send_alert_notification(bot: NotificationBot, alert: Dict):
    """Send notification for a specific alert"""
    parameter = alert.get('parameter', 'unknown')
    severity = alert.get('severity', 'warning')
    message = alert.get('message', 'Alert triggered')
    
    if parameter == 'nu' or parameter == 'beta':
        bot.send_critical_exponent_alert(
            parameter,
            alert.get('value', 0.0),
            alert.get('reference', 0.34),
            alert.get('sigma_deviation', 0.0)
        )
    else:
        # Generic alert
        details = {
            'parameter': parameter,
            'severity': severity,
            'value': alert.get('value'),
            'reference': alert.get('reference')
        }
        
        bot.send_alert(
            'critical_exponent_alert',
            f"Parameter Alert: {parameter}",
            message,
            details,
            severity
        )


if __name__ == "__main__":
    main()
