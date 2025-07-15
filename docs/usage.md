# Usage Guide - Da-P_Satulon

**5分でCA-2Dを可視化**  
Complete guide for running cellular automata experiments and analyzing information conductivity.

## 🚀 Quick Start (5 Minutes)

### 1. Installation & Setup
```bash
# Clone and install
git clone https://github.com/Da-P-AIP/Da-P_Satulon.git
cd Da-P_Satulon
pip install -r requirements.txt

# Verify installation
python -c "from code.ca_2d import CA2D; print('✅ Installation successful!')"
```

### 2. Run Your First Experiment
```bash
# Quick test (30 seconds)
python run_experiments.py --grid-size 20 --iterations 20 --interaction-steps 3 --verbose

# Check results
ls results/run001/
cat results/run001/results_summary.csv
```

### 3. View Results
```bash
# Open plots (macOS/Linux)
open results/run001/plots/summary.png     # macOS
xdg-open results/run001/plots/summary.png # Linux

# Windows
start results/run001/plots/summary.png
```

**🎉 Congratulations!** You've just run your first information conductivity experiment.

---

## 📊 Experiment Types

### Basic Parameter Sweep
```bash
# Standard research experiment
python run_experiments.py \
  --grid-size 50 \
  --iterations 100 \
  --interaction-min 0.1 \
  --interaction-max 1.0 \
  --interaction-steps 10 \
  --conductivity-method entropy \
  --save-plots
```

### Advanced Analysis
```bash
# Comprehensive analysis with all features
python run_experiments.py \
  --grid-size 100 \
  --iterations 200 \
  --interaction-min 0.0 \
  --interaction-max 1.0 \
  --interaction-steps 20 \
  --conductivity-method gradient \
  --multiscale-analysis \
  --save-frames \
  --create-gif \
  --verbose
```

### Comparative Methods
```bash
# Compare different conductivity methods
for method in simple entropy gradient; do
  python run_experiments.py \
    --grid-size 30 \
    --iterations 50 \
    --interaction-steps 5 \
    --conductivity-method $method \
    --run-id "method_${method}"
done
```

---

## 🔬 Python API Usage

### Basic CA Simulation
```python
from code.ca_2d import CA2D, create_ca
from code.ca_2d.info_cond import calculate_information_conductivity

# Create and run CA
ca = create_ca(grid_size=50, interaction_strength=0.5, seed=42)
ca.update(100)

# Calculate conductivity
conductivity = calculate_information_conductivity(ca.grid, method='entropy')
print(f"Information conductivity: {conductivity:.4f}")

# Get time series
series = ca.get_conductivity_series()
print(f"Conductivity evolution: {series[0]:.3f} → {series[-1]:.3f}")
```

### Advanced Analysis
```python
import numpy as np
import matplotlib.pyplot as plt
from code.ca_2d.info_cond import calculate_information_conductivity

# Multi-method comparison
ca = create_ca(30, 0.7, 42)
ca.update(50)

methods = ['simple', 'entropy', 'gradient']
results = {}

for method in methods:
    conductivity = calculate_information_conductivity(ca.grid, method=method)
    results[method] = conductivity
    print(f"{method.capitalize()}: {conductivity:.4f}")

# Multi-scale analysis
multiscale = calculate_information_conductivity(ca.grid, method='multiscale')
for scale, metrics in multiscale.items():
    print(f"{scale}: entropy={metrics['entropy']:.3f}, gradient={metrics['gradient']:.3f}")
```

### Parameter Space Exploration
```python
import pandas as pd

# Systematic parameter exploration
results = []
grid_sizes = [20, 30, 50]
interactions = np.linspace(0.1, 1.0, 5)

for size in grid_sizes:
    for interaction in interactions:
        ca = create_ca(size, interaction, 42)
        ca.update(50)
        
        conductivity = calculate_information_conductivity(ca.grid, method='entropy')
        results.append({
            'grid_size': size,
            'interaction': interaction,
            'conductivity': conductivity
        })

df = pd.DataFrame(results)
print(df.groupby('grid_size')['conductivity'].mean())
```

---

## 📁 Understanding Results

### File Structure
```
results/run001/
├── params.json          # All experiment parameters
├── metadata.json        # Runtime info, dependencies
├── results_summary.csv  # Main results table
├── cond.csv            # Detailed time series
└── plots/
    ├── summary.png      # Main analysis plots
    └── evolution.gif    # Animation (if --create-gif)
```

### Reading Results
```python
import json
import pandas as pd
import numpy as np

# Load experiment parameters
with open('results/run001/params.json') as f:
    params = json.load(f)
print(f"Grid size: {params['grid_size']}")
print(f"Method: {params['conductivity_method']}")

# Load summary results
summary = pd.read_csv('results/run001/results_summary.csv')
print(summary[['interaction_strength', 'conductivity_final', 'conductivity_mean']])

# Load time series
timeseries = pd.read_csv('results/run001/cond.csv')
print(f"Total data points: {len(timeseries)}")

# Find optimal interaction strength
best_idx = summary['conductivity_final'].idxmax()
best_interaction = summary.loc[best_idx, 'interaction_strength']
print(f"Best interaction strength: {best_interaction:.3f}")
```

---

## 🎨 Visualization Examples

### Custom Plotting
```python
import matplotlib.pyplot as plt
import pandas as pd

# Load and plot results
df = pd.read_csv('results/run001/results_summary.csv')

plt.figure(figsize=(12, 4))

# Plot 1: Conductivity vs Interaction
plt.subplot(1, 3, 1)
plt.plot(df['interaction_strength'], df['conductivity_mean'], 'o-')
plt.xlabel('Interaction Strength')
plt.ylabel('Mean Conductivity')
plt.title('Conductivity vs Interaction')
plt.grid(True)

# Plot 2: Evolution trends
plt.subplot(1, 3, 2)
plt.plot(df['interaction_strength'], df['conductivity_trend'], 's-')
plt.xlabel('Interaction Strength')
plt.ylabel('Evolution Trend')
plt.title('Temporal Trends')
plt.grid(True)

# Plot 3: Variability
plt.subplot(1, 3, 3)
plt.errorbar(df['interaction_strength'], df['conductivity_mean'], 
             yerr=df['conductivity_std'], capsize=5)
plt.xlabel('Interaction Strength')
plt.ylabel('Conductivity ± Std')
plt.title('Variability Analysis')
plt.grid(True)

plt.tight_layout()
plt.savefig('custom_analysis.png', dpi=300)
plt.show()
```

### Animation Creation
```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import os

# Load grid states
def load_experiment_frames(run_dir, exp_id=0):
    frames = []
    exp_dir = f"{run_dir}/exp_{exp_id:03d}"
    
    frame_files = sorted([f for f in os.listdir(exp_dir) 
                         if f.startswith('grid_t') and f.endswith('.npy')])
    
    for frame_file in frame_files:
        grid = np.load(f"{exp_dir}/{frame_file}")
        frames.append(grid)
    
    return frames

# Create custom animation
frames = load_experiment_frames('results/run001')

fig, ax = plt.subplots(figsize=(8, 8))

def animate(i):
    ax.clear()
    ax.imshow(frames[i], cmap='viridis', vmin=0, vmax=1)
    ax.set_title(f'Time Step: {i}')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

anim = FuncAnimation(fig, animate, frames=len(frames), interval=100)
anim.save('custom_evolution.gif', writer='pillow', fps=10)
plt.show()
```

---

## 🔧 Advanced Configuration

### Custom Conductivity Methods
```python
from code.ca_2d.info_cond import calculate_information_conductivity

# Method comparison on same data
ca = create_ca(40, 0.6, 123)
ca.update(30)

# Different entropy methods
entropy_hist = calculate_information_conductivity(ca.grid, method='entropy', bins=20)
entropy_gauss = calculate_information_conductivity(ca.grid, method='entropy', method='gaussian')

print(f"Histogram entropy: {entropy_hist:.4f}")
print(f"Gaussian entropy: {entropy_gauss:.4f}")

# Gradient-based analysis with different coupling
grad_weak = calculate_information_conductivity(ca.grid, method='gradient', interaction_strength=0.5)
grad_strong = calculate_information_conductivity(ca.grid, method='gradient', interaction_strength=2.0)

print(f"Weak coupling gradient: {grad_weak:.4f}")
print(f"Strong coupling gradient: {grad_strong:.4f}")
```

### Batch Processing
```python
import glob
import os

# Process multiple experiment runs
def analyze_all_runs(results_dir='results'):
    all_results = []
    
    for run_dir in glob.glob(f"{results_dir}/run*"):
        if os.path.isdir(run_dir):
            summary_file = f"{run_dir}/results_summary.csv"
            
            if os.path.exists(summary_file):
                df = pd.read_csv(summary_file)
                df['run_id'] = os.path.basename(run_dir)
                all_results.append(df)
    
    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        return combined
    return pd.DataFrame()

# Analyze all experiments
all_data = analyze_all_runs()
if not all_data.empty:
    print(f"Total experiments across all runs: {len(all_data)}")
    print(f"Average conductivity: {all_data['conductivity_mean'].mean():.4f}")
    
    # Compare different runs
    run_comparison = all_data.groupby('run_id')['conductivity_mean'].agg(['mean', 'std'])
    print(run_comparison)
```

### Performance Optimization
```python
# For large-scale experiments
import multiprocessing as mp
from functools import partial

def run_parallel_experiments(interaction_values, grid_size=50, iterations=100):
    """Run experiments in parallel"""
    
    def single_experiment(interaction, seed_offset):
        ca = create_ca(grid_size, interaction, 42 + seed_offset)
        ca.update(iterations)
        return calculate_information_conductivity(ca.grid, method='entropy')
    
    # Use multiprocessing
    with mp.Pool() as pool:
        experiment_func = partial(single_experiment, seed_offset=0)
        results = pool.map(experiment_func, interaction_values)
    
    return results

# Example usage for large parameter sweeps
interactions = np.linspace(0.1, 1.0, 50)  # 50 experiments
results = run_parallel_experiments(interactions)
print(f"Completed {len(results)} experiments in parallel")
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'code.ca_2d'
# Solution: Make sure you're in the project root directory
cd Da-P_Satulon
python run_experiments.py

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**2. Memory Issues (Large Grids)**
```python
# For grids larger than 200×200, disable frame saving
python run_experiments.py --grid-size 300 --iterations 100  # No --save-frames

# Or use lower precision
np.random.seed(42)
ca = CA2D(grid_size=(500, 500), interaction_strength=0.5)
ca.grid = ca.grid.astype(np.float32)  # Use float32 instead of float64
```

**3. Plotting Issues**
```python
# If plots don't display (headless environment)
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# For high-DPI displays
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
```

**4. Performance Issues**
```bash
# Reduce computational load
python run_experiments.py \
  --grid-size 30 \        # Smaller grid
  --iterations 50 \       # Fewer steps
  --interaction-steps 5   # Fewer parameter values

# Skip expensive operations
python run_experiments.py --no-multiscale-analysis --no-create-gif
```

### Getting Help

1. **Check CI Status**: Look for green badges in README
2. **Run Tests**: `pytest tests/` to verify installation
3. **Minimal Example**: Try the 5-minute quick start first
4. **Check Logs**: Look at `metadata.json` for system info
5. **Create Issue**: Use GitHub issue templates with error details

---

## 📚 Learning Path

### Beginner (Week 1)
1. Complete 5-minute quick start
2. Run basic parameter sweep
3. Read and understand result files
4. Try different conductivity methods

### Intermediate (Week 2-3)
1. Use Python API for custom analysis
2. Create custom visualizations
3. Understand multi-scale analysis
4. Compare results across experiments

### Advanced (Week 4+)
1. Implement custom conductivity metrics
2. Run large-scale parameter studies
3. Integrate with other analysis tools
4. Contribute to paper writing

---

## 🎯 Research Applications

### Phase Transition Studies
```bash
# Fine-grained analysis around critical points
python run_experiments.py \
  --interaction-min 0.25 \
  --interaction-max 0.35 \
  --interaction-steps 20 \
  --iterations 200 \
  --conductivity-method entropy
```

### Method Validation
```bash
# Compare methods on same data
for method in simple entropy gradient; do
  python run_experiments.py \
    --conductivity-method $method \
    --random-seed 42 \  # Same seed for fair comparison
    --run-id "validation_${method}"
done
```

### Scalability Analysis
```bash
# Test different grid sizes
for size in 20 50 100 200; do
  python run_experiments.py \
    --grid-size $size \
    --iterations 100 \
    --interaction-steps 10 \
    --run-id "scale_${size}"
done
```

---

**Next Steps**: After mastering this guide, explore the [LaTeX paper template](paper_G1/latex/main.tex) and contribute to the research publication!
