#!/usr/bin/env python3
"""
Complete Experiment Runner for Da-P_Satulon CA-2D Research

This script provides comprehensive automated parameter sweeping and result collection
for studying information conductivity in 2D cellular automata.

Implements Issue #3 requirements:
- Full CLI argument support
- Issue #2 compliant data output format
- GIF generation capability
- README code examples compatibility

Usage:
    python run_experiments.py --grid-size 50 --iterations 100 --interaction-min 0.1 --interaction-max 1.0
    python run_experiments.py --help

Author: Da-P-AIP Research Team
Version: 1.0.0 (G1 Phase - Issue #3 Implementation)
"""

import argparse
import json
import os
import sys
import time
import subprocess
import platform
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import warnings

# Import CA-2D implementation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))
try:
    from ca_2d import CA2D, create_ca, calculate_information_conductivity
except ImportError as e:
    print(f"❌ Error importing CA-2D modules: {e}")
    print("   Please ensure Issue #1 (CA-2D implementation) is complete and merged.")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments for experiment parameters"""
    parser = argparse.ArgumentParser(
        description="Run CA-2D experiments with comprehensive parameter sweeping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (README example)
  python run_experiments.py --grid-size 20 --iterations 20 --interaction-steps 3 --verbose
  
  # Research-grade experiment
  python run_experiments.py --grid-size 50 --iterations 100 --interaction-min 0.1 \\
    --interaction-max 1.0 --interaction-steps 10 --conductivity-method entropy \\
    --save-frames --create-gif --verbose
  
  # Phase transition study
  python run_experiments.py --interaction-min 0.25 --interaction-max 0.35 \\
    --interaction-steps 20 --iterations 200 --conductivity-method entropy
  
  # Quick test
  python run_experiments.py --grid-size 10 --iterations 5 --verbose
"""
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
                       choices=['simple', 'entropy', 'gradient', 'temporal', 'multiscale'],
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
    """Generate next available run ID following Issue #2 specification"""
    if not os.path.exists(output_dir):
        return 'run001'
        
    run_dirs = [d for d in os.listdir(output_dir) 
                if d.startswith('run') and os.path.isdir(os.path.join(output_dir, d))]
    if not run_dirs:
        return 'run001'
    
    run_numbers = []
    for d in run_dirs:
        if len(d) == 6 and d[3:].isdigit():  # run001, run002, etc.
            run_numbers.append(int(d[3:]))
    
    next_num = max(run_numbers, default=0) + 1
    return f'run{next_num:03d}'


def create_experiment_config(args, interaction_values: list, run_id: str) -> dict:
    """Create configuration following Issue #2 specification"""
    return {
        "experiment": {
            "run_id": run_id,
            "description": f"CA-2D parameter sweep: {len(interaction_values)} interaction strengths",
            "phase": "G1"
        },
        "ca_parameters": {
            "grid_size": [args.grid_size, args.grid_size],
            "interaction_strength_range": [args.interaction_min, args.interaction_max],
            "interaction_values": interaction_values,
            "boundary_conditions": "zero_flux",
            "initial_conditions": "random_uniform"
        },
        "simulation": {
            "iterations": args.iterations,
            "save_frequency": 1,
            "random_seed": args.random_seed
        },
        "analysis": {
            "conductivity_methods": [args.conductivity_method],
            "save_grids": args.save_frames,
            "create_plots": args.save_plots,
            "create_gif": args.create_gif,
            "multiscale_analysis": args.multiscale_analysis
        },
        "computational": {
            "algorithm_version": "1.0.0",
            "optimization_level": "standard"
        }
    }


def create_metadata(run_id: str, start_time: datetime, end_time: datetime, 
                   experiment_stats: dict) -> dict:
    """Create metadata following Issue #2 specification"""
    duration = (end_time - start_time).total_seconds()
    
    # Get git info if available
    git_commit = "unknown"
    git_branch = "unknown"
    git_dirty = True
    
    try:
        git_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                           stderr=subprocess.DEVNULL).decode().strip()
        git_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                           stderr=subprocess.DEVNULL).decode().strip()
        git_status = subprocess.check_output(['git', 'status', '--porcelain'],
                                           stderr=subprocess.DEVNULL).decode().strip()
        git_dirty = len(git_status) > 0
    except:
        pass
    
    return {
        "execution": {
            "run_id": run_id,
            "start_time": start_time.isoformat() + 'Z',
            "end_time": end_time.isoformat() + 'Z',
            "duration_seconds": duration,
            "hostname": platform.node()
        },
        "environment": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "memory_gb": round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024**3), 1) if hasattr(os, 'sysconf') else "unknown"
        },
        "software": {
            "da_p_satulon_version": "1.0.0",
            "git_commit": git_commit,
            "git_branch": git_branch,
            "is_dirty": git_dirty
        },
        "dependencies": {
            "numpy": np.__version__,
            "matplotlib": plt.matplotlib.__version__,
            "pandas": pd.__version__
        },
        "performance": {
            "total_experiments": experiment_stats.get('total_experiments', 0),
            "avg_experiment_time": experiment_stats.get('avg_experiment_time', 0),
            "total_file_size_mb": experiment_stats.get('total_file_size_mb', 0)
        }
    }


def setup_run_directory(run_dir: str) -> None:
    """Create directory structure following Issue #2 specification"""
    directories = [
        run_dir,
        os.path.join(run_dir, 'grids'),
        os.path.join(run_dir, 'analysis'),
        os.path.join(run_dir, 'plots'),
        os.path.join(run_dir, 'plots', 'grids')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def run_single_experiment(interaction_strength: float, args, run_dir: str, exp_idx: int) -> dict:
    """Run a single CA experiment with given interaction strength"""
    if args.verbose:
        print(f"  Experiment {exp_idx+1}: interaction_strength = {interaction_strength:.3f}")
    
    # Initialize CA with create_ca function (Issue #1 compatibility)
    ca = create_ca(
        grid_size=args.grid_size,
        interaction_strength=interaction_strength,
        seed=args.random_seed + exp_idx  # Different seed per experiment
    )
    
    # Run simulation
    ca.update(args.iterations)
    
    # Calculate conductivity using multiple methods
    conductivity_results = {}
    methods = ['simple', 'entropy', 'gradient']
    
    # Calculate conductivity series for all methods
    for method in methods:
        series = []
        for state in ca.history:
            cond = calculate_information_conductivity(state, method=method)
            series.append(float(cond))
        conductivity_results[f'conductivity_{method}'] = series
    
    # Get grid statistics for each timestep
    mean_activity = [float(np.mean(state)) for state in ca.history]
    std_activity = [float(np.std(state)) for state in ca.history]
    min_activity = [float(np.min(state)) for state in ca.history]
    max_activity = [float(np.max(state)) for state in ca.history]
    
    # Save grid states if requested (only for first experiment to save space)
    if args.save_frames and exp_idx == 0:
        for t, state in enumerate(ca.history):
            filename = f"grid_{t:03d}.npy"
            filepath = os.path.join(run_dir, 'grids', filename)
            np.save(filepath, state.astype(np.float32))
            
            # Create symlinks for convenience (Issue #2 spec)
            if t == 0:
                symlink_path = os.path.join(run_dir, 'grids', 'grid_initial.npy')
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                try:
                    os.symlink(filename, symlink_path)
                except OSError:
                    # Fallback for systems that don't support symlinks
                    import shutil
                    shutil.copy2(filepath, symlink_path)
            elif t == len(ca.history) - 1:
                symlink_path = os.path.join(run_dir, 'grids', 'grid_final.npy')
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                try:
                    os.symlink(filename, symlink_path)
                except OSError:
                    # Fallback for systems that don't support symlinks
                    import shutil
                    shutil.copy2(filepath, symlink_path)
    
    # Multi-scale analysis if requested
    multiscale_results = None
    if args.multiscale_analysis:
        multiscale_results = calculate_information_conductivity(
            ca.grid, method='multiscale'
        )
    
    # Return results in Issue #2 CSV format
    timestep_data = []
    for t in range(len(ca.history)):
        row = {
            'timestep': t,
            'conductivity_simple': conductivity_results['conductivity_simple'][t],
            'conductivity_entropy': conductivity_results['conductivity_entropy'][t],
            'conductivity_gradient': conductivity_results['conductivity_gradient'][t],
            'mean_activity': mean_activity[t],
            'std_activity': std_activity[t],
            'min_activity': min_activity[t],
            'max_activity': max_activity[t],
            'interaction_strength': interaction_strength
        }
        timestep_data.append(row)
    
    return {
        'experiment_id': exp_idx,
        'interaction_strength': interaction_strength,
        'timestep_data': timestep_data,
        'multiscale_results': multiscale_results,
        'ca_stats': ca.get_statistics()
    }


def main():
    """Main experiment runner implementing Issue #3 requirements"""
    args = parse_arguments()
    
    print("=== Da-P_Satulon Enhanced Experiment Runner ===")
    print("Issue #3 Implementation: Full CLI + Issue #2 Data Format + GIF Generation")
    print(f"Grid size: {args.grid_size}×{args.grid_size}")
    print(f"Iterations: {args.iterations}")
    print(f"Interaction range: {args.interaction_min} - {args.interaction_max} ({args.interaction_steps} steps)")
    print(f"Conductivity method: {args.conductivity_method}")
    print(f"Random seed: {args.random_seed}")
    
    # Setup output directory
    os.makedirs(args.output_dir, exist_ok=True)
    run_id = args.run_id or get_next_run_id(args.output_dir)
    run_dir = os.path.join(args.output_dir, run_id)
    setup_run_directory(run_dir)
    
    print(f"Output directory: {run_dir}")
    
    # Generate interaction strength values
    if args.interaction_steps == 1:
        interaction_values = [args.interaction_min]
    else:
        interaction_values = np.linspace(args.interaction_min, args.interaction_max, args.interaction_steps)
    
    # Save configuration (Issue #2 format)
    config = create_experiment_config(args, interaction_values.tolist(), run_id)
    config_path = os.path.join(run_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Record start time
    start_time = datetime.utcnow()
    
    # Run experiments with progress bar
    print(f"\nRunning {len(interaction_values)} experiments...")
    results = []
    
    if args.verbose:
        for i, interaction in enumerate(interaction_values):
            result = run_single_experiment(interaction, args, run_dir, i)
            results.append(result)
    else:
        for i, interaction in enumerate(tqdm(interaction_values, desc="Experiments")):
            result = run_single_experiment(interaction, args, run_dir, i)
            results.append(result)
    
    # Record end time
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    # Calculate experiment statistics
    all_final_conductivities = [r['timestep_data'][-1]['conductivity_simple'] for r in results]
    experiment_stats = {
        'total_experiments': len(results),
        'avg_experiment_time': duration / len(results),
        'total_file_size_mb': 0  # Would calculate actual file sizes in production
    }
    
    # Save metadata
    metadata = create_metadata(run_id, start_time, end_time, experiment_stats)
    metadata_path = os.path.join(run_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Save results following Issue #2 specification
    all_timestep_data = []
    for result in results:
        all_timestep_data.extend(result['timestep_data'])
    
    # Save main results_summary.csv
    df = pd.DataFrame(all_timestep_data)
    summary_path = os.path.join(run_dir, 'results_summary.csv')
    df.to_csv(summary_path, index=False)
    
    # Save analysis statistics
    analysis_stats = {
        'summary': {
            'total_experiments': len(results),
            'interaction_strengths': [r['interaction_strength'] for r in results],
            'final_conductivities': {
                'simple': [r['timestep_data'][-1]['conductivity_simple'] for r in results],
                'entropy': [r['timestep_data'][-1]['conductivity_entropy'] for r in results],
                'gradient': [r['timestep_data'][-1]['conductivity_gradient'] for r in results]
            }
        }
    }
    
    analysis_path = os.path.join(run_dir, 'analysis', 'statistics.json')
    with open(analysis_path, 'w') as f:
        json.dump(analysis_stats, f, indent=2)
    
    # Create summary plots if requested
    if args.save_plots:
        plots_dir = os.path.join(run_dir, 'plots')
        
        # Extract data for plotting
        interactions = [r['interaction_strength'] for r in results]
        final_simple = [r['timestep_data'][-1]['conductivity_simple'] for r in results]
        final_entropy = [r['timestep_data'][-1]['conductivity_entropy'] for r in results]
        final_gradient = [r['timestep_data'][-1]['conductivity_gradient'] for r in results]
        
        # Create main summary plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Information Conductivity Analysis\\n'
                    f'Grid: {args.grid_size}×{args.grid_size}, Iterations: {args.iterations}', 
                    fontsize=14)
        
        # Method comparison
        ax1 = axes[0, 0]
        ax1.plot(interactions, final_simple, 'o-', label='Simple', linewidth=2)
        ax1.plot(interactions, final_entropy, 's-', label='Entropy', linewidth=2)
        ax1.plot(interactions, final_gradient, '^-', label='Gradient', linewidth=2)
        ax1.set_xlabel('Interaction Strength')
        ax1.set_ylabel('Final Conductivity')
        ax1.set_title('Conductivity Methods Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Time evolution for selected experiments
        ax2 = axes[0, 1]
        selected_indices = [0, len(results)//2, -1] if len(results) > 2 else range(len(results))
        for idx in selected_indices:
            if idx < len(results):
                result = results[idx]
                timesteps = [d['timestep'] for d in result['timestep_data']]
                simple_series = [d['conductivity_simple'] for d in result['timestep_data']]
                ax2.plot(timesteps, simple_series, alpha=0.8, 
                        label=f"ρ={result['interaction_strength']:.2f}")
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Information Conductivity (Simple)')
        ax2.set_title('Time Evolution (Selected)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Method correlation
        ax3 = axes[1, 0]
        ax3.scatter(final_simple, final_entropy, alpha=0.7, s=50)
        ax3.set_xlabel('Simple Conductivity')
        ax3.set_ylabel('Entropy Conductivity')
        ax3.set_title('Simple vs Entropy Methods')
        
        # Add correlation line
        if len(final_simple) > 1:
            correlation = np.corrcoef(final_simple, final_entropy)[0, 1]
            ax3.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                     transform=ax3.transAxes, bbox=dict(boxstyle="round", facecolor='wheat'))
        ax3.grid(True, alpha=0.3)
        
        # Statistical summary
        ax4 = axes[1, 1]
        methods = ['Simple', 'Entropy', 'Gradient']
        means = [np.mean(final_simple), np.mean(final_entropy), np.mean(final_gradient)]
        stds = [np.std(final_simple), np.std(final_entropy), np.std(final_gradient)]
        
        bars = ax4.bar(methods, means, yerr=stds, capsize=5, alpha=0.7, 
                       color=['blue', 'green', 'red'])
        ax4.set_ylabel('Mean Final Conductivity')
        ax4.set_title('Method Statistics')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{mean:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        summary_path = os.path.join(plots_dir, 'summary.png')
        plt.savefig(summary_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  Plots saved to {plots_dir}/summary.png")
    
    # Create GIF animation if requested
    if args.create_gif and args.save_frames:
        grids_dir = os.path.join(run_dir, 'grids')
        if os.path.exists(grids_dir):
            grid_files = sorted([f for f in os.listdir(grids_dir) 
                                if f.startswith('grid_') and f.endswith('.npy') 
                                and f not in ['grid_initial.npy', 'grid_final.npy']])
            
            if len(grid_files) >= 2:
                print("  Creating evolution GIF animation...")
                sample_rate = max(1, len(grid_files) // 30)
                sampled_files = grid_files[::sample_rate]
                
                fig, ax = plt.subplots(figsize=(8, 8))
                
                def animate(frame_idx):
                    ax.clear()
                    if frame_idx < len(sampled_files):
                        grid_file = sampled_files[frame_idx]
                        grid_path = os.path.join(grids_dir, grid_file)
                        grid = np.load(grid_path)
                        
                        im = ax.imshow(grid, cmap='viridis', vmin=0, vmax=1)
                        timestep = int(grid_file.split('_')[1].split('.')[0])
                        ax.set_title(f'CA Evolution - Step {timestep}\\n'
                                    f'Grid: {grid.shape[0]}×{grid.shape[1]}')
                        ax.set_xlabel('X')
                        ax.set_ylabel('Y')
                        
                        if frame_idx == 0:
                            plt.colorbar(im, ax=ax, label='Cell State', shrink=0.8)
                    return []
                
                anim = FuncAnimation(fig, animate, frames=len(sampled_files), 
                                    interval=300, blit=False, repeat=True)
                
                gif_path = os.path.join(run_dir, 'plots', 'evolution.gif')
                try:
                    anim.save(gif_path, writer='pillow', fps=3)
                    print(f"  GIF saved: {gif_path}")
                except Exception as e:
                    print(f"  Warning: Could not save GIF: {e}")
                finally:
                    plt.close()
    
    # Print comprehensive summary
    print(f"\n=== Experiment Complete ===")
    print(f"Total runtime: {duration:.2f} seconds ({duration/60:.1f} minutes)")
    print(f"Results saved to: {run_dir}")
    
    # Key findings
    best_idx = np.argmax(all_final_conductivities)
    best_result = results[best_idx]
    
    print(f"\nKey findings:")
    print(f"  Experiments run: {len(results)}")
    print(f"  Grid size: {args.grid_size}×{args.grid_size}")
    print(f"  Iterations per experiment: {args.iterations}")
    print(f"  Best interaction strength: {best_result['interaction_strength']:.3f}")
    print(f"  Best simple conductivity: {all_final_conductivities[best_idx]:.4f}")
    print(f"  Conductivity range: {min(all_final_conductivities):.4f} - {max(all_final_conductivities):.4f}")
    print(f"  Average conductivity: {np.mean(all_final_conductivities):.4f}")
    
    print(f"\nFiles created (Issue #2 compliant):")
    print(f"  📊 {run_dir}/results_summary.csv")
    print(f"  ⚙️  {run_dir}/config.json")
    print(f"  📋 {run_dir}/metadata.json")
    print(f"  📈 {run_dir}/analysis/statistics.json")
    if args.save_plots:
        print(f"  🎨 {run_dir}/plots/summary.png")
    if args.save_frames:
        grids_count = len([f for f in os.listdir(os.path.join(run_dir, 'grids')) if f.endswith('.npy')]) if os.path.exists(os.path.join(run_dir, 'grids')) else 0
        if grids_count > 0:
            print(f"  💾 {run_dir}/grids/ ({grids_count} grid files)")
    if args.create_gif and args.save_frames:
        print(f"  🎬 {run_dir}/plots/evolution.gif")
    
    print(f"\nNext steps:")
    print(f"  • Load results: pandas.read_csv('{run_dir}/results_summary.csv')")
    print(f"  • View plots: open {run_dir}/plots/")
    print(f"  • Analyze data: python -c \"import sys; sys.path.append('code'); from ca_2d import *\"")


if __name__ == "__main__":
    main()
