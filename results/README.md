# Data Output Specification (G1 Phase)

**Version: 1.1 - Issue #2 Implementation**

This document defines the standardized format for experimental results in the Da-P_Satulon project, supporting reproducible research and systematic analysis.

## Directory Structure

```
results/
├── README.md              # This specification document
├── run001/                # Experiment run (auto-generated ID)
│   ├── config.json        # Experiment parameters & settings
│   ├── metadata.json      # Run metadata (timestamps, environment)
│   ├── grids/             # Grid state files
│   │   ├── grid_000.npy   # Initial grid state (timestep 0)
│   │   ├── grid_001.npy   # Grid state at timestep 1
│   │   ├── grid_002.npy   # Grid state at timestep 2
│   │   ├── ...
│   │   └── grid_final.npy # Final grid state (symlink or copy)
│   ├── results_summary.csv    # Main results: conductivity time series
│   ├── analysis/          # Analysis outputs
│   │   ├── statistics.json    # Comprehensive statistics
│   │   └── conductivity_methods.csv # Multi-method comparison
│   └── plots/             # Visualization outputs
│       ├── evolution.gif      # Time evolution animation
│       ├── conductivity.png   # Conductivity vs time plot
│       ├── summary.png        # Summary dashboard
│       └── grids/             # Individual timestep plots
│           ├── grid_000.png
│           ├── grid_010.png
│           └── ...
├── run002/                # Next experiment run
├── ...
└── .run_counter           # Internal: tracks next run ID
```

## File Format Specifications

### 1. Grid States (`grids/grid_*.npy`)

**Purpose**: Store cellular automaton grid states at each timestep

```python
# Format Details
- File Format: NumPy binary (.npy)
- Shape: (height, width) for 2D CA
- Data Type: float32 (memory efficient, sufficient precision)
- Value Range: [0.0, 1.0] (normalized cell states)
- Compression: None (NPY is already efficient)

# Naming Convention
- grid_000.npy  # Initial state (t=0)
- grid_001.npy  # After 1 update
- grid_final.npy  # Symlink to last timestep for convenience

# Loading Example
import numpy as np
grid_t5 = np.load('results/run001/grids/grid_005.npy')
print(f"Grid shape: {grid_t5.shape}")  # e.g., (50, 50)
print(f"Value range: [{grid_t5.min():.3f}, {grid_t5.max():.3f}]")
```

### 2. Results Summary (`results_summary.csv`)

**Purpose**: Main experimental results with time series data

```csv
timestep,conductivity_simple,conductivity_entropy,conductivity_gradient,mean_activity,std_activity,min_activity,max_activity,interaction_strength
0,0.4932,0.7845,0.2156,0.4932,0.2889,0.0013,0.9987,0.5
1,0.4931,0.7842,0.2158,0.4931,0.2885,0.0015,0.9985,0.5
2,0.4929,0.7838,0.2161,0.4929,0.2881,0.0018,0.9982,0.5
3,0.4926,0.7834,0.2165,0.4926,0.2876,0.0021,0.9979,0.5
4,0.4923,0.7829,0.2169,0.4923,0.2871,0.0024,0.9976,0.5
```

**Column Descriptions**:
- `timestep`: Simulation timestep (0, 1, 2, ...)
- `conductivity_simple`: Simple mean-based conductivity
- `conductivity_entropy`: Shannon entropy-based conductivity
- `conductivity_gradient`: Spatial gradient-based conductivity
- `mean_activity`: Average cell value across grid
- `std_activity`: Standard deviation of cell values
- `min_activity`, `max_activity`: Range of cell values
- `interaction_strength`: CA interaction parameter (constant per run)

### 3. Configuration (`config.json`)

**Purpose**: Complete experiment configuration for reproducibility

```json
{
  "experiment": {
    "run_id": "run001",
    "description": "Baseline CA-2D experiment with medium interaction strength",
    "phase": "G1"
  },
  "ca_parameters": {
    "grid_size": [50, 50],
    "interaction_strength": 0.5,
    "boundary_conditions": "zero_flux",
    "initial_conditions": "random_uniform"
  },
  "simulation": {
    "iterations": 100,
    "save_frequency": 1,
    "random_seed": 42
  },
  "analysis": {
    "conductivity_methods": ["simple", "entropy", "gradient"],
    "save_grids": true,
    "create_plots": true,
    "create_gif": true
  },
  "computational": {
    "algorithm_version": "1.1.0",
    "optimization_level": "standard"
  }
}
```

### 4. Metadata (`metadata.json`)

**Purpose**: Execution environment and provenance information

```json
{
  "execution": {
    "run_id": "run001",
    "start_time": "2025-07-15T04:15:30.123Z",
    "end_time": "2025-07-15T04:18:45.456Z",
    "duration_seconds": 195.333,
    "hostname": "research-workstation-01"
  },
  "environment": {
    "python_version": "3.9.7",
    "platform": "Linux-5.4.0-x86_64",
    "cpu_count": 8,
    "memory_gb": 32
  },
  "software": {
    "da_p_satulon_version": "0.1.1",
    "git_commit": "1f892bb38702779f13ea4a9b2ebdbfa61c7a6043",
    "git_branch": "g1/ca-2d-core",
    "is_dirty": false
  },
  "dependencies": {
    "numpy": "1.24.3",
    "matplotlib": "3.7.1",
    "scipy": "1.10.1"
  },
  "performance": {
    "peak_memory_mb": 245.7,
    "avg_cpu_percent": 15.3,
    "total_file_size_mb": 12.4
  }
}
```

### 5. Statistics (`analysis/statistics.json`)

**Purpose**: Comprehensive statistical analysis of the run

```json
{
  "summary": {
    "final_conductivity_simple": 0.4901,
    "final_conductivity_entropy": 0.7812,
    "final_conductivity_gradient": 0.2187,
    "conductivity_trend_simple": -0.0031,
    "convergence_timestep": 85,
    "system_stability": "converged"
  },
  "grid_statistics": {
    "initial": {
      "mean": 0.4932,
      "std": 0.2889,
      "entropy": 0.7845,
      "spatial_correlation": 0.0123
    },
    "final": {
      "mean": 0.4901,
      "std": 0.2876,
      "entropy": 0.7812,
      "spatial_correlation": 0.1567
    }
  },
  "temporal_evolution": {
    "settling_time": 78,
    "oscillation_amplitude": 0.0012,
    "trend_significance": 0.03
  }
}
```

### 6. Method Comparison (`analysis/conductivity_methods.csv`)

**Purpose**: Detailed comparison of different conductivity calculation methods

```csv
method,final_value,mean_value,std_value,trend_slope,convergence_time,stability_metric
simple,0.4901,0.4916,0.0089,−0.000031,85,0.92
entropy,0.7812,0.7828,0.0156,−0.000021,78,0.94
gradient,0.2187,0.2174,0.0067,0.000013,92,0.89
multiscale_1,0.4901,0.4916,0.0089,−0.000031,85,0.92
multiscale_2,0.4523,0.4537,0.0078,−0.000028,88,0.91
multiscale_4,0.3987,0.4001,0.0065,−0.000024,82,0.93
```

## Naming Conventions

### Run IDs
- **Format**: `run{:03d}` (zero-padded 3 digits)
- **Examples**: `run001`, `run002`, `run123`
- **Auto-increment**: Based on `.run_counter` file or existing directories
- **Maximum**: `run999` (can be extended if needed)

### Grid Files
- **Timesteps**: `grid_{:03d}.npy` (e.g., `grid_000.npy`, `grid_001.npy`)
- **Special files**: 
  - `grid_initial.npy` → symlink to `grid_000.npy`
  - `grid_final.npy` → symlink to last timestep

### Plot Files
- **Required plots**:
  - `evolution.gif` - Complete time evolution animation
  - `conductivity.png` - All conductivity methods vs time
  - `summary.png` - Dashboard with key metrics
- **Optional plots**:
  - `grids/grid_{:03d}.png` - Individual timestep visualizations
  - `phase_space.png` - Phase space analysis (if applicable)
  - `correlation.png` - Spatial correlation analysis

## Implementation Guidelines

### Creating New Experiments

```python
import os
import json
import numpy as np
from datetime import datetime

def create_experiment_run(config):
    """Create a new experiment run directory with proper structure"""
    
    # Get next run ID
    run_id = get_next_run_id()
    run_dir = f"results/{run_id}"
    
    # Create directory structure
    os.makedirs(f"{run_dir}/grids", exist_ok=True)
    os.makedirs(f"{run_dir}/analysis", exist_ok=True) 
    os.makedirs(f"{run_dir}/plots/grids", exist_ok=True)
    
    # Save configuration
    config['experiment']['run_id'] = run_id
    with open(f"{run_dir}/config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    # Initialize metadata
    metadata = create_metadata_template(run_id)
    with open(f"{run_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return run_dir

def save_grid_state(run_dir, timestep, grid):
    """Save grid state with proper naming"""
    filename = f"{run_dir}/grids/grid_{timestep:03d}.npy"
    np.save(filename, grid.astype(np.float32))
    
    # Create symlinks for convenience
    if timestep == 0:
        os.symlink(f"grid_000.npy", f"{run_dir}/grids/grid_initial.npy")
```

### Loading and Analysis

```python
def load_experiment_run(run_id):
    """Load complete experiment run for analysis"""
    run_dir = f"results/{run_id}"
    
    # Load configuration and metadata
    with open(f"{run_dir}/config.json") as f:
        config = json.load(f)
    
    with open(f"{run_dir}/metadata.json") as f:
        metadata = json.load(f)
    
    # Load main results
    import pandas as pd
    results = pd.read_csv(f"{run_dir}/results_summary.csv")
    
    # Load analysis if available
    analysis = {}
    if os.path.exists(f"{run_dir}/analysis/statistics.json"):
        with open(f"{run_dir}/analysis/statistics.json") as f:
            analysis['statistics'] = json.load(f)
    
    if os.path.exists(f"{run_dir}/analysis/conductivity_methods.csv"):
        analysis['methods'] = pd.read_csv(f"{run_dir}/analysis/conductivity_methods.csv")
    
    return {
        'config': config,
        'metadata': metadata,
        'results': results,
        'analysis': analysis,
        'run_dir': run_dir
    }

def load_grid_sequence(run_id, timesteps=None):
    """Load sequence of grid states"""
    run_dir = f"results/{run_id}"
    
    if timesteps is None:
        # Auto-detect available timesteps
        grid_files = glob.glob(f"{run_dir}/grids/grid_*.npy")
        timesteps = sorted([int(f.split('_')[-1].split('.')[0]) 
                           for f in grid_files if 'grid_' in f and f[-4:] == '.npy'])
    
    grids = []
    for t in timesteps:
        grid = np.load(f"{run_dir}/grids/grid_{t:03d}.npy")
        grids.append(grid)
    
    return np.array(grids), timesteps
```

## Sample Data Examples

### Sample run001/ Directory

To demonstrate the specification, here's what a complete run001 directory should look like:

```
results/run001/
├── config.json           # 2.1 KB - Experiment configuration
├── metadata.json         # 1.8 KB - Environment & provenance
├── grids/                # ~15 MB total for 100 timesteps (50x50 grid)
│   ├── grid_000.npy      # 10.0 KB - Initial state
│   ├── grid_001.npy      # 10.0 KB - After 1 iteration
│   ├── grid_002.npy      # 10.0 KB - After 2 iterations
│   ├── ...               # ... (98 more files)
│   ├── grid_099.npy      # 10.0 KB - Final state
│   ├── grid_initial.npy  # Symlink → grid_000.npy
│   └── grid_final.npy    # Symlink → grid_099.npy
├── results_summary.csv   # 8.5 KB - Time series data (100 rows)
├── analysis/
│   ├── statistics.json   # 1.2 KB - Statistical summary
│   └── conductivity_methods.csv # 0.8 KB - Method comparison
└── plots/
    ├── evolution.gif     # 2.5 MB - Animation (compressed)
    ├── conductivity.png  # 150 KB - Time series plot
    ├── summary.png       # 200 KB - Dashboard
    └── grids/           # ~5 MB total (selective timesteps)
        ├── grid_000.png  # 50 KB - Initial visualization
        ├── grid_010.png  # 50 KB - After 10 steps
        ├── grid_025.png  # 50 KB - After 25 steps
        ├── grid_050.png  # 50 KB - Mid-point
        ├── grid_075.png  # 50 KB - Near end
        └── grid_099.png  # 50 KB - Final state

Total size: ~25 MB per experiment run
```

## Validation and Quality Assurance

### File Validation

```python
def validate_experiment_run(run_id):
    """Validate that an experiment run meets specification"""
    run_dir = f"results/{run_id}"
    
    # Required files check
    required_files = [
        'config.json',
        'metadata.json', 
        'results_summary.csv'
    ]
    
    for file in required_files:
        if not os.path.exists(f"{run_dir}/{file}"):
            raise ValueError(f"Missing required file: {file}")
    
    # Check grid consistency
    config = json.load(open(f"{run_dir}/config.json"))
    iterations = config['simulation']['iterations']
    
    expected_grids = list(range(iterations + 1))  # 0 to iterations
    for t in expected_grids:
        grid_file = f"{run_dir}/grids/grid_{t:03d}.npy"
        if not os.path.exists(grid_file):
            raise ValueError(f"Missing grid file: grid_{t:03d}.npy")
    
    print(f"✅ Run {run_id} validation passed")
```

### Data Integrity Checks

```python
def check_data_integrity(run_id):
    """Check data integrity and consistency"""
    run_dir = f"results/{run_id}"
    
    # Load and validate CSV structure
    df = pd.read_csv(f"{run_dir}/results_summary.csv")
    required_columns = [
        'timestep', 'conductivity_simple', 'conductivity_entropy',
        'conductivity_gradient', 'mean_activity', 'std_activity'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column in results_summary.csv: {col}")
    
    # Check for NaN values
    if df.isnull().any().any():
        raise ValueError("Found NaN values in results_summary.csv")
    
    # Validate timestep sequence
    expected_timesteps = list(range(len(df)))
    if not df['timestep'].tolist() == expected_timesteps:
        raise ValueError("Timestep sequence is not continuous")
    
    print(f"✅ Data integrity check passed for {run_id}")
```

## Migration and Compatibility

### Version Compatibility

- **v1.0**: Basic specification (original)
- **v1.1**: Enhanced with analysis subdirectory, improved metadata
- **Future versions**: Will maintain backward compatibility where possible

### Migration Scripts

```python
def migrate_v1_0_to_v1_1(run_id):
    """Migrate older result format to v1.1"""
    run_dir = f"results/{run_id}"
    
    # Create new directory structure
    os.makedirs(f"{run_dir}/analysis", exist_ok=True)
    
    # Move old cond.csv to results_summary.csv if exists
    if os.path.exists(f"{run_dir}/cond.csv"):
        os.rename(f"{run_dir}/cond.csv", f"{run_dir}/results_summary.csv")
    
    print(f"✅ Migrated {run_id} to v1.1 format")
```

## Best Practices

### Performance Optimization

1. **Storage Efficiency**:
   - Use `float32` for grid states (sufficient precision, 50% smaller than `float64`)
   - Compress large GIF animations
   - Only save visualization plots for key timesteps

2. **Memory Management**:
   - Load grids on-demand rather than keeping full sequence in memory
   - Use memory mapping for large grid sequences
   - Clear intermediate arrays in analysis scripts

3. **I/O Optimization**:
   - Batch file operations when possible
   - Use asynchronous I/O for saving multiple files
   - Consider using HDF5 for very large experiments (G2+ phases)

### Research Reproducibility

1. **Complete Provenance**:
   - Always include git commit hash
   - Record all dependency versions
   - Include random seeds and initialization states

2. **Documentation**:
   - Add descriptive comments to config.json
   - Include experimental hypothesis in metadata
   - Document any manual post-processing steps

3. **Validation**:
   - Run integrity checks after each experiment
   - Maintain checksums for critical result files
   - Verify results can be loaded and analyzed

## Future Extensions (G2+ Phases)

### Planned Enhancements

1. **3D Support**: Extended grid format for 3D cellular automata
2. **Parallel Runs**: Support for parameter sweep batches
3. **Advanced Analysis**: Phase space, bifurcation analysis
4. **Interactive Visualization**: Web-based result browsers
5. **Database Integration**: Metadata stored in database for querying

### Scalability Considerations

- **Large Grids**: HDF5 format for grids > 500×500
- **Long Runs**: Compressed storage for runs > 10,000 timesteps  
- **High-Throughput**: Automated analysis pipelines
- **Cloud Storage**: S3/cloud-compatible file organization

---

**Document Version**: 1.1  
**Last Updated**: 2025-07-15  
**Author**: Da-P-AIP Research Team  
**Status**: G1 Implementation Complete
