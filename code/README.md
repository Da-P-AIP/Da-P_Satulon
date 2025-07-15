# Code Implementation Guide

This directory contains the core implementation of the Da-P_Satulon research project.

## Quick Start

### Running the CA-2D Example
```bash
# Navigate to project root
cd Da-P_Satulon

# Run basic CA-2D example
python code/ca_2d/grid.py
```

### Running Parameter Sweep Experiments
```bash
# Simple experiment
python run_experiments.py --grid-size 30 --iterations 50

# Full parameter sweep
python run_experiments.py \
  --grid-size 50 \
  --iterations 100 \
  --interaction-min 0.1 \
  --interaction-max 1.0 \
  --interaction-steps 10 \
  --save-frames \
  --create-gif
```

## Current Implementation Status (G1 Phase)

### ✅ Completed
- **Basic CA-2D Class Structure** (`ca_2d/grid.py`)
  - Grid initialization and management
  - Update mechanism (stub implementation)
  - Information conductivity calculation (stub)
  - History tracking for analysis
  
- **Experiment Runner** (`run_experiments.py`)
  - Command-line parameter interface
  - Automated parameter sweeping
  - Result collection and CSV export
  - Basic visualization and plotting
  - Metadata and configuration saving

### 🔄 In Progress (Issue #1)
- **CA Update Rules**: Currently using simple diffusion-like update
- **Information Conductivity**: Placeholder using grid mean
- **Proper CA Dynamics**: Need to implement actual cellular automaton rules

### ⏳ Planned (Issues #2-#5)
- **Advanced Metrics**: More sophisticated information measures
- **Enhanced Visualization**: GIF animations, interactive plots
- **CI/CD Pipeline**: Automated testing and quality assurance
- **Documentation**: Comprehensive API docs

## Code Structure

```
code/
├── ca_2d/
│   ├── grid.py          # Main CA-2D implementation
│   └── utils.py         # Utility functions (future)
└── ca_3d/              # 3D extension (G3+ phases)
```

## API Reference

### CA2D Class

```python
from code.ca_2d.grid import CA2D

# Initialize
ca = CA2D(grid_size=(50, 50), interaction_strength=0.5, random_seed=42)

# Run simulation
ca.update(iterations=100)

# Get results
conductivity = ca.information_conductivity()
series = ca.get_conductivity_series()
state = ca.get_state(timestep=10)  # Get specific timestep
```

### Experiment Runner

```python
# From command line
python run_experiments.py --help

# Key parameters:
#   --grid-size N          # Grid size (NxN)
#   --iterations N         # Number of CA steps
#   --interaction-min X    # Min interaction strength
#   --interaction-max Y    # Max interaction strength
#   --interaction-steps N  # Number of values to test
#   --output-dir PATH      # Where to save results
#   --save-frames          # Save .npy grid states
#   --create-gif           # Generate animations
```

## Development Workflow

### 1. Making Changes
```bash
# Create feature branch
git checkout -b g1/feature-name

# Make changes to code
# Test locally
python code/ca_2d/grid.py

# Commit and push
git add .
git commit -m "Implement feature X for Issue #N"
git push origin g1/feature-name
```

### 2. Creating Pull Requests
- Reference the issue: "Closes #1"
- Include test results
- Update documentation if needed

### 3. Testing Your Changes
```bash
# Basic functionality test
python code/ca_2d/grid.py

# Parameter sweep test
python run_experiments.py --grid-size 10 --iterations 5

# Check output
ls results/run*/
```

## Extending the Code

### Adding New CA Rules
```python
# In ca_2d/grid.py, modify _single_update() method
def _single_update(self) -> None:
    # Your custom CA update rules here
    # Example: Conway's Game of Life rules
    # Example: Reaction-diffusion equations
    pass
```

### Adding New Metrics
```python
# In ca_2d/grid.py, enhance information_conductivity() method
def information_conductivity(self) -> float:
    # Your custom information theory metrics
    # Example: Mutual information
    # Example: Transfer entropy
    # Example: Integrated information
    pass
```

### Adding New Visualization
```python
# In run_experiments.py, enhance create_summary_plots()
def create_summary_plots(results, run_dir):
    # Add new plot types
    # Example: Phase diagrams
    # Example: Correlation matrices
    # Example: Network analysis plots
    pass
```

## Performance Notes

### Current Limitations (G1 Phase)
- **Memory**: Grid states stored in history (O(iterations × grid_size²))
- **Speed**: Pure Python implementation (no optimization yet)
- **Scalability**: Not optimized for large grids or long simulations

### Future Optimizations (G2+ Phases)
- NumPy vectorization for CA updates
- Memory-efficient state storage
- Optional GPU acceleration with CuPy
- Parallel parameter sweeping

## Troubleshooting

### Common Issues

**ImportError: No module named 'grid'**
```bash
# Make sure you're in the project root
cd Da-P_Satulon
python code/ca_2d/grid.py
```

**Empty results directory**
```bash
# Check if output directory exists
ls -la results/
# Run with explicit output directory
python run_experiments.py --output-dir ./results
```

**Matplotlib backend errors**
```bash
# For headless environments
export MPLBACKEND=Agg
python run_experiments.py
```

### Getting Help

1. Check the [Issues](https://github.com/Da-P-AIP/Da-P_Satulon/issues) for similar problems
2. Create a new issue with:
   - Error message
   - Steps to reproduce
   - System information (Python version, OS)

## Contributing Guidelines

1. **Code Style**: Follow PEP 8 (enforced by flake8 in CI)
2. **Documentation**: Add docstrings to all functions and classes
3. **Testing**: Add tests for new functionality (when CI is set up)
4. **Performance**: Consider scalability for large-scale experiments

---

**Note**: This is G1 phase code with stub implementations. Major enhancements are planned for subsequent phases.
