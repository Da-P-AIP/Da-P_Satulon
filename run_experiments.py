#!/usr/bin/env python3
"""
Enhanced Automated Experiment Runner for Da-P_Satulon CA-2D Research

This script provides automated parameter sweeping and result collection
for studying information conductivity in 2D cellular automata.

Enhanced Features:
- Multiple conductivity calculation methods
- Comprehensive parameter logging
- Optional GIF generation
- Improved result analysis and visualization

Usage:
    python run_experiments.py --grid-size 50 --iterations 100 --interaction-min 0.1 --interaction-max 1.0

Author: Da-P-AIP Research Team
Version: 0.2.0 (G1 Phase Enhanced)
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
from tqdm import tqdm
import warnings

# Import CA-2D implementation
import sys
sys.path.append('code/ca_2d')
from grid import CA2D
from info_cond import calculate_information_conductivity


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
    parser.add_argument('--conductivity-method', type=str, default='simple',
                       choices=['simple', 'entropy', 'gradient', 'temporal'],
                       help='Method for calculating information conductivity')
    
    # Analysis options
    parser.add_argument('--multiscale-analysis', action='store_true',
                       help='Perform multi-scale conductivity analysis')
    parser.add_argument('--save-plots', action='store_true', default=True,
                       help='Save summary plots')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    return parser.parse_args()


def get_next_run_id(output_dir: str) -> str:
    """Generate next available run ID"""
    if not os.path.exists(output_dir):
        return 'run001'
        
    run_dirs = [d for d in os.listdir(output_dir) 
                if d.startswith('run') and os.path.isdir(os.path.join(output_dir, d))]
    if not run_dirs:
        return 'run001'
    
    run_numbers = [int(d[3:]) for d in run_dirs if d[3:].isdigit()]
    next_num = max(run_numbers, default=0) + 1
    return f'run{next_num:03d}'


def save_experiment_config(run_dir: str, args, interaction_values: list) -> dict:
    """Save comprehensive experiment configuration to JSON file"""
    config = {
        # Basic parameters
        'grid_size': [args.grid_size, args.grid_size],
        'iterations': args.iterations,
        'interaction_strength_range': [args.interaction_min, args.interaction_max],
        'interaction_values': interaction_values,
        'interaction_steps': args.interaction_steps,
        'random_seed': args.random_seed,
        
        # Analysis parameters
        'conductivity_method': args.conductivity_method,
        'multiscale_analysis': args.multiscale_analysis,
        'save_frames': args.save_frames,
        'create_gif': args.create_gif,
        
        # Version and metadata
        'algorithm_version': '0.2.0-enhanced',
        'experiment_type': 'parameter_sweep',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    config_path = os.path.join(run_dir, 'params.json')  # Changed from config.json
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config


def save_metadata(run_dir: str, start_time: datetime, end_time: datetime, 
                 experiment_stats: dict) -> None:
    """Save comprehensive experiment metadata"""
    duration = (end_time - start_time).total_seconds()
    
    metadata = {
        'run_id': os.path.basename(run_dir),
        'start_time': start_time.isoformat() + 'Z',
        'end_time': end_time.isoformat() + 'Z',
        'duration_seconds': duration,
        'duration_human': f"{int(duration//60):02d}:{int(duration%60):02d}",
        
        # System info
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'dependencies': {
            'numpy': np.__version__,
            'matplotlib': plt.matplotlib.__version__,
            'pandas': pd.__version__
        },
        
        # Experiment statistics
        'total_experiments': experiment_stats.get('total_experiments', 0),
        'total_ca_steps': experiment_stats.get('total_ca_steps', 0),
        'avg_conductivity': experiment_stats.get('avg_conductivity', 0),
        'conductivity_range': experiment_stats.get('conductivity_range', [0, 0])
    }
    
    metadata_path = os.path.join(run_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def run_single_experiment(interaction_strength: float, args, run_dir: str, exp_idx: int) -> dict:
    """Run a single CA experiment with given interaction strength"""
    if args.verbose:
        print(f"  Running experiment {exp_idx+1}: interaction_strength = {interaction_strength:.3f}")
    
    # Initialize CA
    ca = CA2D(
        grid_size=(args.grid_size, args.grid_size),
        interaction_strength=interaction_strength,
        random_seed=args.random_seed + exp_idx  # Different seed per experiment
    )
    
    # Run simulation
    ca.update(args.iterations)
    
    # Calculate conductivity using specified method
    if args.conductivity_method == 'temporal':
        conductivity_series = calculate_information_conductivity(
            ca.history, method='temporal', method='simple'
        )
    else:
        # Calculate for each time step
        conductivity_series = []
        for state in ca.history:
            cond = calculate_information_conductivity(
                state, method=args.conductivity_method
            )
            conductivity_series.append(cond)
        conductivity_series = np.array(conductivity_series)
    
    # Multi-scale analysis if requested
    multiscale_results = None
    if args.multiscale_analysis:
        multiscale_results = calculate_information_conductivity(
            ca.grid, method='multiscale'
        )
    
    # Save grid states if requested
    if args.save_frames:
        exp_dir = os.path.join(run_dir, f'exp_{exp_idx:03d}')
        os.makedirs(exp_dir, exist_ok=True)
        
        for t, state in enumerate(ca.history):
            np.save(os.path.join(exp_dir, f'grid_t{t:04d}.npy'), state)
    
    # Calculate summary statistics
    conductivity_stats = {
        'final': float(conductivity_series[-1]),
        'mean': float(np.mean(conductivity_series)),
        'std': float(np.std(conductivity_series)),
        'min': float(np.min(conductivity_series)),
        'max': float(np.max(conductivity_series)),
        'trend': float(conductivity_series[-1] - conductivity_series[0]),
        'variance': float(np.var(conductivity_series))
    }
    
    # Return comprehensive results
    result = {
        'experiment_id': exp_idx,
        'interaction_strength': interaction_strength,
        'conductivity_method': args.conductivity_method,
        'conductivity_stats': conductivity_stats,
        'conductivity_series': conductivity_series.tolist(),
        'grid_final_shape': ca.grid.shape,
        'total_steps': len(ca.history)
    }
    
    if multiscale_results:
        result['multiscale_analysis'] = multiscale_results
    
    return result


def create_enhanced_plots(results: list, run_dir: str, args) -> None:
    """Create comprehensive visualization plots"""
    plots_dir = os.path.join(run_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Extract data for plotting
    interactions = [r['interaction_strength'] for r in results]
    final_conds = [r['conductivity_stats']['final'] for r in results]
    mean_conds = [r['conductivity_stats']['mean'] for r in results]
    std_conds = [r['conductivity_stats']['std'] for r in results]
    trends = [r['conductivity_stats']['trend'] for r in results]
    
    # Main summary plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Information Conductivity Analysis - Method: {args.conductivity_method}', 
                fontsize=16)
    
    # Conductivity vs Interaction Strength
    ax1 = axes[0, 0]
    ax1.errorbar(interactions, mean_conds, yerr=std_conds, 
                 marker='o', capsize=5, label='Mean ± Std')
    ax1.plot(interactions, final_conds, 's-', alpha=0.7, label='Final')
    ax1.set_xlabel('Interaction Strength')
    ax1.set_ylabel('Information Conductivity')
    ax1.set_title('Conductivity vs Interaction')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Evolution trends
    ax2 = axes[0, 1]
    ax2.plot(interactions, trends, 'go-', linewidth=2)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Interaction Strength')
    ax2.set_ylabel('Conductivity Trend')
    ax2.set_title('Evolution Trend')
    ax2.grid(True, alpha=0.3)
    
    # Time series for selected experiments
    ax3 = axes[1, 0]
    for i, result in enumerate(results[::max(1, len(results)//5)]):  # Show max 5 series
        series = result['conductivity_series']
        time_steps = range(len(series))
        ax3.plot(time_steps, series, alpha=0.8, 
                label=f"ρ={result['interaction_strength']:.2f}")
    ax3.set_xlabel('Time Step')
    ax3.set_ylabel('Information Conductivity')
    ax3.set_title('Time Evolution (Selected)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Statistical distribution
    ax4 = axes[1, 1]
    ax4.hist(mean_conds, bins=min(10, len(mean_conds)), alpha=0.7, 
             color='skyblue', edgecolor='black')
    ax4.axvline(np.mean(mean_conds), color='red', linestyle='--', 
                label=f'Overall Mean: {np.mean(mean_conds):.3f}')
    ax4.set_xlabel('Mean Conductivity')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Conductivity Distribution')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'summary.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Enhanced plots saved to {plots_dir}/")


def create_gif_animation(results: list, run_dir: str, args) -> None:
    """Create GIF animation of CA evolution"""
    if not args.create_gif or not args.save_frames:
        return
    
    print("  Creating evolution GIF animation...")
    plots_dir = os.path.join(run_dir, 'plots')
    
    # Use the first experiment for GIF
    exp_dir = os.path.join(run_dir, 'exp_000')
    if not os.path.exists(exp_dir):
        print("    Warning: No frame data found for GIF creation")
        return
    
    # Load frame files
    frame_files = sorted([f for f in os.listdir(exp_dir) if f.startswith('grid_t') and f.endswith('.npy')])
    if len(frame_files) < 2:
        print("    Warning: Not enough frames for GIF")
        return
    
    # Create animation
    fig, ax = plt.subplots(figsize=(8, 8))
    
    def animate(frame_idx):
        ax.clear()
        frame_file = frame_files[min(frame_idx, len(frame_files)-1)]
        grid = np.load(os.path.join(exp_dir, frame_file))
        
        im = ax.imshow(grid, cmap='viridis', vmin=0, vmax=1)
        ax.set_title(f'CA Evolution - Step {frame_idx}\n'
                    f'Interaction Strength: {results[0]["interaction_strength"]:.3f}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        if frame_idx == 0:
            plt.colorbar(im, ax=ax, label='Cell State')
        
        return [im]
    
    # Create animation with sampling for reasonable file size
    sample_rate = max(1, len(frame_files) // 50)  # Max 50 frames
    sampled_frames = range(0, len(frame_files), sample_rate)
    
    anim = FuncAnimation(fig, animate, frames=sampled_frames, 
                        interval=200, blit=False, repeat=True)
    
    gif_path = os.path.join(plots_dir, 'evolution.gif')
    anim.save(gif_path, writer='pillow', fps=5)
    plt.close()
    
    print(f"    GIF saved: {gif_path}")


def save_detailed_csv(results: list, run_dir: str) -> None:
    """Save detailed experiment results to CSV files"""
    # Summary CSV
    summary_data = []
    for r in results:
        row = {
            'experiment_id': r['experiment_id'],
            'interaction_strength': r['interaction_strength'],
            'conductivity_method': r['conductivity_method'],
            **{f'conductivity_{k}': v for k, v in r['conductivity_stats'].items()}
        }
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    summary_csv_path = os.path.join(run_dir, 'results_summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    
    # Detailed time series CSV
    detailed_data = []
    for r in results:
        for t, cond_val in enumerate(r['conductivity_series']):
            detailed_data.append({
                'experiment_id': r['experiment_id'],
                'interaction_strength': r['interaction_strength'],
                'timestep': t,
                'conductivity': cond_val
            })
    
    detailed_df = pd.DataFrame(detailed_data)
    detailed_csv_path = os.path.join(run_dir, 'cond.csv')  # Standard name from results/README.md
    detailed_df.to_csv(detailed_csv_path, index=False)
    
    print(f"  Results saved: {summary_csv_path}")
    print(f"  Time series saved: {detailed_csv_path}")


def main():
    """Enhanced main experiment runner"""
    args = parse_arguments()
    
    print("=== Da-P_Satulon Enhanced Experiment Runner ===")
    print(f"Grid size: {args.grid_size}×{args.grid_size}")
    print(f"Iterations: {args.iterations}")
    print(f"Interaction range: {args.interaction_min} - {args.interaction_max}")
    print(f"Conductivity method: {args.conductivity_method}")
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
    config = save_experiment_config(run_dir, args, interaction_values.tolist())
    
    # Record start time
    start_time = datetime.utcnow()
    
    # Run experiments with progress bar
    print(f"\nRunning {len(interaction_values)} experiments...")
    results = []
    
    progress_bar = tqdm(enumerate(interaction_values), total=len(interaction_values), 
                       desc="Experiments") if not args.verbose else enumerate(interaction_values)
    
    for i, interaction in progress_bar:
        result = run_single_experiment(interaction, args, run_dir, i)
        results.append(result)
    
    # Record end time
    end_time = datetime.utcnow()
    
    # Calculate experiment statistics
    all_conductivities = [r['conductivity_stats']['mean'] for r in results]
    experiment_stats = {
        'total_experiments': len(results),
        'total_ca_steps': sum(r['total_steps'] for r in results),
        'avg_conductivity': float(np.mean(all_conductivities)),
        'conductivity_range': [float(np.min(all_conductivities)), float(np.max(all_conductivities))]
    }
    
    # Save results and metadata
    save_detailed_csv(results, run_dir)
    save_metadata(run_dir, start_time, end_time, experiment_stats)
    
    if args.save_plots:
        create_enhanced_plots(results, run_dir, args)
    
    if args.create_gif:
        create_gif_animation(results, run_dir, args)
    
    # Print comprehensive summary
    duration = (end_time - start_time).total_seconds()
    print(f"\n=== Experiment Complete ===")
    print(f"Total runtime: {duration:.2f} seconds")
    print(f"Results saved to: {run_dir}")
    print(f"Summary plots: {run_dir}/plots/")
    
    # Key findings
    best_result = max(results, key=lambda x: x['conductivity_stats']['final'])
    worst_result = min(results, key=lambda x: x['conductivity_stats']['final'])
    
    print(f"\nKey findings:")
    print(f"  Method used: {args.conductivity_method}")
    print(f"  Best interaction strength: {best_result['interaction_strength']:.3f}")
    print(f"  Best final conductivity: {best_result['conductivity_stats']['final']:.4f}")
    print(f"  Conductivity range: {experiment_stats['conductivity_range'][0]:.4f} - {experiment_stats['conductivity_range'][1]:.4f}")
    print(f"  Average conductivity: {experiment_stats['avg_conductivity']:.4f}")
    
    print("\nFiles created:")
    print(f"  📊 {run_dir}/results_summary.csv")
    print(f"  📈 {run_dir}/cond.csv")
    print(f"  ⚙️  {run_dir}/params.json")
    print(f"  📋 {run_dir}/metadata.json")
    if args.save_plots:
        print(f"  🎨 {run_dir}/plots/summary.png")
    if args.create_gif and args.save_frames:
        print(f"  🎬 {run_dir}/plots/evolution.gif")
    
    print("\nUse the results for further analysis or publication!")


if __name__ == "__main__":
    main()
