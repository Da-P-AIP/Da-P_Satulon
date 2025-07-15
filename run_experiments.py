#!/usr/bin/env python3
"""
Automated Experiment Runner for Da-P_Satulon CA-2D Research

This script provides automated parameter sweeping and result collection
for studying information conductivity in 2D cellular automata.

Usage:
    python run_experiments.py --grid-size 50 --iterations 100 --interaction-min 0.1 --interaction-max 1.0

Author: Da-P-AIP Research Team
Version: 0.1.0 (G1 Phase - Stub Implementation)
"""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Import CA-2D implementation
import sys
sys.path.append('code/ca_2d')
from grid import CA2D


def parse_arguments():
    """Parse command line arguments for experiment parameters"""
    parser = argparse.ArgumentParser(
        description="Run CA-2D experiments with parameter sweeping",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Grid parameters
    parser.add_argument('--grid-size', type=int, default=50,
                       help='Size of the square grid (NxN)')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of CA update iterations')
    
    # Interaction strength sweep
    parser.add_argument('--interaction-min', type=float, default=0.1,
                       help='Minimum interaction strength')
    parser.add_argument('--interaction-max', type=float, default=1.0,
                       help='Maximum interaction strength')
    parser.add_argument('--interaction-steps', type=int, default=5,
                       help='Number of interaction strength values to test')
    
    # Output configuration
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for results')
    parser.add_argument('--run-id', type=str, default=None,
                       help='Custom run ID (auto-generated if not provided)')
    
    # Execution options
    parser.add_argument('--random-seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--save-frames', action='store_true',
                       help='Save individual grid states as .npy files')
    parser.add_argument('--create-gif', action='store_true',
                       help='Create evolution animation GIF')
    
    return parser.parse_args()


def get_next_run_id(output_dir: str) -> str:
    """Generate next available run ID"""
    run_dirs = [d for d in os.listdir(output_dir) if d.startswith('run') and os.path.isdir(os.path.join(output_dir, d))]
    if not run_dirs:
        return 'run001'
    
    run_numbers = [int(d[3:]) for d in run_dirs if d[3:].isdigit()]
    next_num = max(run_numbers, default=0) + 1
    return f'run{next_num:03d}'


def save_experiment_config(run_dir: str, args, interaction_values: list) -> dict:
    """Save experiment configuration to JSON file"""
    config = {
        'grid_size': [args.grid_size, args.grid_size],
        'iterations': args.iterations,
        'interaction_strength_range': [args.interaction_min, args.interaction_max],
        'interaction_values': interaction_values,
        'interaction_steps': args.interaction_steps,
        'random_seed': args.random_seed,
        'algorithm_version': '0.1.0-stub',
        'experiment_type': 'parameter_sweep'
    }
    
    config_path = os.path.join(run_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config


def save_metadata(run_dir: str, start_time: datetime, end_time: datetime) -> None:
    """Save experiment metadata"""
    duration = (end_time - start_time).total_seconds()
    
    metadata = {
        'run_id': os.path.basename(run_dir),
        'start_time': start_time.isoformat() + 'Z',
        'end_time': end_time.isoformat() + 'Z',
        'duration_seconds': duration,
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'dependencies': {
            'numpy': np.__version__,
            'matplotlib': plt.matplotlib.__version__,
            'pandas': pd.__version__
        }
    }
    
    metadata_path = os.path.join(run_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def run_single_experiment(interaction_strength: float, args, run_dir: str, exp_idx: int) -> dict:
    """Run a single CA experiment with given interaction strength"""
    print(f"  Running experiment {exp_idx+1}: interaction_strength = {interaction_strength:.3f}")
    
    # Initialize CA
    ca = CA2D(
        grid_size=(args.grid_size, args.grid_size),
        interaction_strength=interaction_strength,
        random_seed=args.random_seed + exp_idx  # Different seed per experiment
    )
    
    # Run simulation
    ca.update(args.iterations)
    
    # Calculate conductivity series
    conductivity_series = ca.get_conductivity_series()
    
    # Save grid states if requested
    if args.save_frames:
        exp_dir = os.path.join(run_dir, f'exp_{exp_idx:03d}')
        os.makedirs(exp_dir, exist_ok=True)
        
        for t, state in enumerate(ca.history):
            np.save(os.path.join(exp_dir, f'grid_{t:03d}.npy'), state)
    
    # Return results
    return {
        'experiment_id': exp_idx,
        'interaction_strength': interaction_strength,
        'final_conductivity': conductivity_series[-1],
        'mean_conductivity': np.mean(conductivity_series),
        'conductivity_trend': conductivity_series[-1] - conductivity_series[0],
        'conductivity_variance': np.var(conductivity_series),
        'conductivity_series': conductivity_series.tolist()
    }


def create_summary_plots(results: list, run_dir: str) -> None:
    """Create summary visualization plots"""
    plots_dir = os.path.join(run_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Extract data for plotting
    interactions = [r['interaction_strength'] for r in results]
    final_conds = [r['final_conductivity'] for r in results]
    mean_conds = [r['mean_conductivity'] for r in results]
    trends = [r['conductivity_trend'] for r in results]
    
    # 1. Conductivity vs Interaction Strength
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.plot(interactions, final_conds, 'bo-', label='Final')
    plt.plot(interactions, mean_conds, 'ro-', label='Mean')
    plt.xlabel('Interaction Strength')
    plt.ylabel('Information Conductivity')
    plt.title('Conductivity vs Interaction')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 2)
    plt.plot(interactions, trends, 'go-')
    plt.xlabel('Interaction Strength')
    plt.ylabel('Conductivity Trend')
    plt.title('Evolution Trend')
    plt.grid(True)
    
    # 3. Time series for all experiments
    plt.subplot(1, 3, 3)
    for i, result in enumerate(results):
        series = result['conductivity_series']
        plt.plot(series, alpha=0.7, label=f"ρ={result['interaction_strength']:.2f}")
    
    plt.xlabel('Time Step')
    plt.ylabel('Information Conductivity')
    plt.title('Time Evolution')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'summary.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Summary plots saved to {plots_dir}/")


def save_results_csv(results: list, run_dir: str) -> None:
    """Save experiment results to CSV file"""
    # Create summary DataFrame
    summary_data = []
    for r in results:
        summary_data.append({
            'experiment_id': r['experiment_id'],
            'interaction_strength': r['interaction_strength'],
            'final_conductivity': r['final_conductivity'],
            'mean_conductivity': r['mean_conductivity'],
            'conductivity_trend': r['conductivity_trend'],
            'conductivity_variance': r['conductivity_variance']
        })
    
    df = pd.DataFrame(summary_data)
    csv_path = os.path.join(run_dir, 'results_summary.csv')
    df.to_csv(csv_path, index=False)
    
    print(f"  Results summary saved to {csv_path}")


def main():
    """Main experiment runner"""
    args = parse_arguments()
    
    print("=== Da-P_Satulon Automated Experiment Runner ===")
    print(f"Grid size: {args.grid_size}x{args.grid_size}")
    print(f"Iterations: {args.iterations}")
    print(f"Interaction range: {args.interaction_min} - {args.interaction_max}")
    print(f"Random seed: {args.random_seed}")
    
    # Setup output directory
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = args.run_id or get_next_run_id(args.output_dir)
    run_dir = os.path.join(args.output_dir, run_id)
    os.makedirs(run_dir, exist_ok=True)
    
    print(f"Output directory: {run_dir}")
    
    # Generate interaction strength values
    interaction_values = np.linspace(args.interaction_min, args.interaction_max, args.interaction_steps)
    
    # Save configuration
    save_experiment_config(run_dir, args, interaction_values.tolist())
    
    # Record start time
    start_time = datetime.utcnow()
    
    # Run experiments
    print(f"\\nRunning {len(interaction_values)} experiments...")
    results = []
    
    for i, interaction in enumerate(interaction_values):
        result = run_single_experiment(interaction, args, run_dir, i)
        results.append(result)
    
    # Record end time
    end_time = datetime.utcnow()
    
    # Save results and metadata
    save_results_csv(results, run_dir)
    save_metadata(run_dir, start_time, end_time)
    create_summary_plots(results, run_dir)
    
    # Print summary
    duration = (end_time - start_time).total_seconds()
    print(f"\\n=== Experiment Complete ===")
    print(f"Total runtime: {duration:.2f} seconds")
    print(f"Results saved to: {run_dir}")
    print(f"Summary plots: {run_dir}/plots/")
    
    # Print key findings
    best_interaction = max(results, key=lambda x: x['final_conductivity'])
    print(f"\\nKey findings:")
    print(f"  Best interaction strength: {best_interaction['interaction_strength']:.3f}")
    print(f"  Best final conductivity: {best_interaction['final_conductivity']:.4f}")
    
    print("\\nUse the results for further analysis or publication!")


if __name__ == "__main__":
    main()
