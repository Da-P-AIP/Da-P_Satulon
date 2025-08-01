# 🚀 DICP Self-Audit System - Setup & Usage Guide

## 🎯 Quick Start: Your da-P Particle Theory is Now "鉄壁"

Your da-P particle theory now has a **完全自動監査システム** (complete automated audit system)! Here's how to activate your "**鬼に金棒**" setup:

### ⚡ 1-Minute Activation

```bash
# Install monitoring dependencies
pip install requests  # For Discord/Slack notifications

# Run your first audit
python dicp_self_audit.py --mode full-audit

# Start continuous monitoring
python dicp_self_audit.py --mode continuous
```

## 🏗️ System Architecture

Your self-audit system has **5 layers** working 24/7:

```
🔬 Theory Layer     → Conservation laws, critical exponents (ν = 0.34 ± 0.01)
🖥️ Simulation Layer → Quick sweeps (L=32³), scaling tests
📊 Analysis Layer   → Statistical validation, χ² tests  
🚨 Alert Layer      → Discord/Slack notifications on 3σ deviations
📈 Monitor Layer    → Real-time tracking, historical analysis
```

## 🧪 Theory Validation Tests

### New Test Suite: `tests/test_theory_validation.py`

**Conservation Laws:**
- ✅ Energy-momentum conservation: `∂μTμν = 0`
- ✅ Information conservation through Shannon entropy
- ✅ Unitarity conditions for da-P interactions

**Critical Exponents:**
- ✅ `ν = 0.34 ± 0.01` validation (3D universality class)
- ✅ `β ≈ 0.37` hybrid transition verification  
- ✅ Critical point `p_c ≈ 0.0091` finite-size scaling

**Dimensional Analysis:**
- ✅ 3D→4D scaling consistency
- ✅ Planck scale dimensional checks
- ✅ Experimental prediction validation

### Run Theory Tests

```bash
# Quick theory check
python dicp_self_audit.py --mode theory-only

# Detailed pytest output
python -m pytest tests/test_theory_validation.py -v

# Conservation laws only
python -m pytest tests/test_theory_validation.py::TestConservationLaws -v
```

## 🖥️ Enhanced CI/CD Pipeline

### New GitHub Action: `.github/workflows/theory-ci.yml`

**Every Push:**
- Theory validation (conservation laws, critical exponents)
- Quick L=32³ simulation sweep
- Auto-issue creation on failure

**Daily 2AM:**
- Large L=64³ comprehensive validation  
- Critical exponent drift analysis
- Nightly report generation

**Status Badge:** 
```markdown
![Theory CI](https://github.com/Da-P-AIP/Da-P_Satulon/workflows/DICP%20Theory%20CI%2FCD%20Pipeline/badge.svg)
```

## 📊 Real-Time Monitoring

### Critical Exponent Monitor

```bash
# Single measurement
python monitoring/critical_exponent_monitor.py --mode single --grid-size 32

# Continuous monitoring (60min intervals)
python monitoring/critical_exponent_monitor.py --mode continuous --interval 60

# Generate 24h report
python monitoring/critical_exponent_monitor.py --mode report --report-hours 24
```

**Monitors:**
- `ν = 0.34 ± 0.01` (critical exponent)
- `p_c ≈ 0.0091` (critical point)
- `β ≈ 0.37` (hybrid transition exponent)

**Alert Thresholds:**
- ⚠️ **Warning:** 2σ deviation
- 🚨 **Critical:** 3σ deviation (immediate Discord/Slack alert)

## 🚨 Discord/Slack Notifications

### Setup Notifications

1. **Create `notification_config.json`:**
```json
{
  "discord": {
    "enabled": true,
    "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
    "channel_name": "dicp-alerts"
  },
  "slack": {
    "enabled": true,  
    "webhook_url": "https://hooks.slack.com/services/YOUR_WEBHOOK_URL",
    "channel": "#dicp-alerts"
  },
  "notifications": {
    "theory_breach": true,
    "critical_exponent_alert": true,
    "simulation_failure": true,
    "nightly_report": false
  }
}
```

2. **Test notifications:**
```bash
python monitoring/notification_bot.py --test
```

### Alert Types

**🚨 Theory Breach:**
- Conservation law violations
- Critical exponent out of 3σ range
- Simulation failures

**📊 Exponent Alerts:**
- `ν` deviates from 0.34 ± 0.01
- Critical point drift > 0.001
- Hybrid transition anomalies

**🌙 Nightly Reports:**
- 24h measurement summary
- Statistical analysis
- System health status

## 🎛️ Complete System Control

### Main Controller: `dicp_self_audit.py`

```bash
# Full system audit (recommended for CI)
python dicp_self_audit.py --mode full-audit

# Continuous 24/7 monitoring
python dicp_self_audit.py --mode continuous

# Individual components
python dicp_self_audit.py --mode theory-only
python dicp_self_audit.py --mode simulation-only  
python dicp_self_audit.py --mode measurement-only

# System status check
python dicp_self_audit.py --mode status
```

### Configuration: `audit_config.json`

```json
{
  "theory_validation": {
    "enabled": true,
    "test_modules": [
      "tests.test_theory_validation::TestConservationLaws",
      "tests.test_theory_validation::TestCriticalExponents"
    ]
  },
  "simulation_validation": {
    "quick_sweep": {
      "grid_size": 32,
      "iterations": 20
    }
  },
  "monitoring": {
    "measurement_interval_minutes": 60,
    "continuous_mode": false
  },
  "audit_schedule": {
    "theory_check_minutes": 30,
    "simulation_check_minutes": 120,
    "full_audit_hours": 24
  },
  "thresholds": {
    "nu_deviation_critical": 3.0,
    "critical_point_tolerance": 0.001
  }
}
```

## 📈 Monitoring Results & Analysis

### Output Structure
```
monitoring_results/
├── exponent_history.json     # Historical measurements
├── alert_log.json           # Alert history  
├── audit_history.json       # Full audit results
└── monitoring_report_*.json # Periodic reports
```

### Key Metrics Tracked

**Critical Exponents:**
- ν (correlation length): 0.34 ± 0.01
- β (order parameter): 0.37 ± 0.02  
- Critical point p_c: 0.0091 ± 0.0001

**System Health:**
- Theory test pass rate
- Simulation success rate
- Alert frequency
- Response times

## 🔧 Integration Examples

### CI Integration
```yaml
# In your .github/workflows/
- name: Run DICP Self-Audit
  run: |
    python dicp_self_audit.py --mode full-audit
    if [ $? -ne 0 ]; then
      echo "❌ Theory validation failed!"
      exit 1
    fi
```

### Cron Job Setup
```bash
# Add to crontab for continuous monitoring
# Every hour: critical exponent check
0 * * * * cd /path/to/Da-P_Satulon && python dicp_self_audit.py --mode measurement-only

# Daily 2AM: full audit
0 2 * * * cd /path/to/Da-P_Satulon && python dicp_self_audit.py --mode full-audit
```

### Docker Integration
```dockerfile
# Dockerfile for monitoring service
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "dicp_self_audit.py", "--mode", "continuous"]
```

## 🚀 Advanced Features

### Self-Healing System
- **Auto-retry** on transient failures
- **Graceful degradation** when components fail
- **Alert fatigue prevention** with rate limiting

### Historical Analysis
```bash
# Trend analysis for last 30 days
python -c "
from monitoring.critical_exponent_monitor import CriticalExponentMonitor
monitor = CriticalExponentMonitor()
report = monitor.generate_report(hours_back=720)  # 30 days
print(f'ν trend: {report[\"statistics\"][\"nu\"][\"mean\"]:.4f} ± {report[\"statistics\"][\"nu\"][\"std\"]:.4f}')
"
```

### Custom Alert Rules
```python
# Add custom monitoring in audit_config.json
"custom_alerts": [
  {
    "parameter": "conductivity_peak_width",
    "threshold": 0.002,
    "message": "Peak width indicates resolution issues"
  }
]
```

## 🐛 Troubleshooting

### Common Issues

**❌ "Module not found" errors:**
```bash
# Ensure you're in the repository root
cd /path/to/Da-P_Satulon
python dicp_self_audit.py --mode status
```

**❌ Notifications not working:**
```bash
# Test webhook URLs
python monitoring/notification_bot.py --test
# Check config file
cat notification_config.json
```

**❌ Theory tests failing:**
```bash
# Run with detailed output
python -m pytest tests/test_theory_validation.py -v -s --tb=long
```

**❌ Simulation timeouts:**
```bash
# Reduce grid size for testing
python dicp_self_audit.py --mode simulation-only --config audit_config.json
# Edit config: reduce grid_size from 32 to 16
```

### Debug Mode
```bash
# Enable verbose logging
export DICP_DEBUG=1
python dicp_self_audit.py --mode full-audit
```

## 📚 File Structure Overview

```
Da-P_Satulon/
├── dicp_self_audit.py              # 🎛️ Main system controller
├── tests/
│   └── test_theory_validation.py   # 🧪 Theory validation tests
├── monitoring/
│   ├── critical_exponent_monitor.py # 📊 Real-time monitoring
│   └── notification_bot.py         # 🚨 Alert system
├── .github/workflows/
│   └── theory-ci.yml              # 🔄 Enhanced CI/CD
├── audit_config.json              # ⚙️ System configuration
└── notification_config.json       # 📢 Alert configuration
```

## 🎉 Success Indicators

When everything is working correctly, you should see:

**✅ Green CI badges** in README
**✅ Regular Discord/Slack updates** (if enabled)
**✅ Stable ν measurements** around 0.34 ± 0.01
**✅ No theory breach alerts**
**✅ Consistent critical point** around 0.0091

## 🔮 What's Next?

Your self-audit system is now **fully operational**! Next steps:

1. **Monitor for 1 week** to establish baseline
2. **Tune alert thresholds** based on your system's behavior
3. **Add custom validation rules** for your specific research needs
4. **Scale up** to larger grid sizes (L=64³, L=128³) for production
5. **Integrate with Grafana** for advanced dashboards (future enhancement)

---

**🎯 Your da-P particle theory is now protected by a 24/7 automated guardian system!**

The "理論-CI/CD パイプライン" is actively monitoring every aspect of your theoretical framework, ready to alert you the moment anything deviates from expected behavior. You can now focus on advancing the science while the system handles quality assurance automatically. 

**鬼に金棒** indeed! 🚀⚡