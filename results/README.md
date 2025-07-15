# Data Output Specification

This document defines the standardized format for experimental results in the Da-P_Satulon project.

## Directory Structure

```
results/
├── README.md              # This file
├── run001/                # Experiment run (auto-generated ID)
│   ├── config.json        # Experiment parameters
│   ├── grid_000.npy       # Grid state at timestep 0
│   ├── grid_001.npy       # Grid state at timestep 1
│   ├── ...
│   ├── grid_final.npy     # Final grid state
│   ├── cond.csv           # Information conductivity time series
│   ├── metadata.json      # Run metadata (timestamps, version, etc.)
│   └── plots/             # Visualization outputs
│       ├── evolution.gif  # Time evolution animation
│       ├── conductivity.png # Conductivity vs time plot
│       └── summary.png    # Summary statistics
├── run002/
└── ...
```

## File Formats

### 1. Grid States (`grid_*.npy`)
- **Format**: NumPy binary (.npy)
- **Shape**: `(height, width)` for 2D CA
- **Data Type**: `float32` or `int32`
- **Content**: Cell states at specific timestep

### 2. Information Conductivity (`cond.csv`)
```csv
timestep,conductivity,mean_activity,variance
0,0.123,0.456,0.789
1,0.124,0.457,0.788
...
```

### 3. Configuration (`config.json`)
```json
{
  "grid_size": [50, 50],
  "iterations": 100,
  "interaction_strength": 0.5,
  "initial_conditions": "random",
  "random_seed": 12345,
  "algorithm_version": "1.0.0"
}
```

### 4. Metadata (`metadata.json`)
```json
{
  "run_id": "run001",
  "start_time": "2025-07-15T02:30:00Z",
  "end_time": "2025-07-15T02:35:00Z",
  "duration_seconds": 300,
  "git_commit": "abc123def",
  "python_version": "3.9.0",
  "dependencies": {
    "numpy": "1.21.0",
    "matplotlib": "3.5.0"
  }
}
```

## Naming Conventions

### Run IDs
- Format: `run{:03d}` (e.g., run001, run002, ...)
- Auto-increment based on existing directories

### Grid Files
- Format: `grid_{:03d}.npy` for timesteps
- Special: `grid_initial.npy`, `grid_final.npy`

### Plot Files
- `evolution.gif` - Time evolution animation
- `conductivity.png` - Main metrics plot
- `summary.png` - Summary statistics
- Custom plots: `{description}.png`

## Usage Examples

### Loading Results
```python
import numpy as np
import pandas as pd
import json

# Load grid state
grid = np.load('results/run001/grid_010.npy')

# Load conductivity data
cond_data = pd.read_csv('results/run001/cond.csv')

# Load configuration
with open('results/run001/config.json') as f:
    config = json.load(f)
```

### Creating New Run Directory
```python
def create_run_directory():
    run_id = get_next_run_id()  # Auto-increment
    run_dir = f"results/{run_id}"
    os.makedirs(f"{run_dir}/plots", exist_ok=True)
    return run_dir
```

## Version History

- **v1.0** (G1 Phase): Initial specification
- Future versions will be documented here

## Notes

- All timestamps use ISO 8601 format (UTC)
- File sizes optimized for storage efficiency
- Compatible with standard scientific Python stack
- Extensible for future 3D implementations