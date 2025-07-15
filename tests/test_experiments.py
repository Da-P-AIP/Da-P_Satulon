"""
Unit tests for run_experiments.py functionality

This module tests the experiment runner and CLI interface to ensure
proper parameter handling and output generation.

Run with: pytest tests/test_experiments.py
"""

import pytest
import subprocess
import tempfile
import json
import os
import pandas as pd
import shutil
from pathlib import Path


class TestExperimentRunner:
    """Test cases for the experiment runner script"""
    
    def test_help_option(self):
        """Test that --help option works"""
        result = subprocess.run(
            ['python', 'run_experiments.py', '--help'],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        assert result.returncode == 0
        assert 'usage:' in result.stdout.lower() or 'usage:' in result.stderr.lower()
        assert '--grid-size' in result.stdout or '--grid-size' in result.stderr
    
    def test_basic_experiment_execution(self):
        """Test basic experiment execution with minimal parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '5',
                '--iterations', '2',
                '--interaction-steps', '2',
                '--output-dir', temp_dir,
                '--verbose'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            # Should complete successfully
            assert result.returncode == 0, f"Command failed with: {result.stderr}"
            
            # Check if output directory was created
            results_dirs = [d for d in os.listdir(temp_dir) if d.startswith('run')]
            assert len(results_dirs) > 0, "No run directory created"
            
            run_dir = os.path.join(temp_dir, results_dirs[0])
            
            # Check required files exist
            required_files = ['config.json', 'metadata.json', 'results_summary.csv']
            for file_name in required_files:
                file_path = os.path.join(run_dir, file_name)
                assert os.path.exists(file_path), f"Required file missing: {file_name}"
    
    def test_custom_run_id(self):
        """Test custom run ID specification"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_id = 'test_custom_123'
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '4',
                '--iterations', '2',
                '--interaction-steps', '2',
                '--output-dir', temp_dir,
                '--run-id', custom_id
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            
            # Check custom run ID was used
            custom_dir = os.path.join(temp_dir, custom_id)
            assert os.path.exists(custom_dir), f"Custom run directory not created: {custom_id}"
    
    def test_interaction_parameter_range(self):
        """Test interaction strength parameter range"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '5',
                '--iterations', '2',
                '--interaction-min', '0.2',
                '--interaction-max', '0.8',
                '--interaction-steps', '3',
                '--output-dir', temp_dir
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            
            # Verify interaction values in config
            run_dirs = [d for d in os.listdir(temp_dir) if d.startswith('run')]
            config_path = os.path.join(temp_dir, run_dirs[0], 'config.json')
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            interaction_values = config['ca_parameters']['interaction_values']
            assert len(interaction_values) == 3
            assert min(interaction_values) >= 0.2
            assert max(interaction_values) <= 0.8
    
    def test_conductivity_methods(self):
        """Test different conductivity calculation methods"""
        methods = ['simple', 'entropy', 'gradient']
        
        for method in methods:
            with tempfile.TemporaryDirectory() as temp_dir:
                result = subprocess.run([
                    'python', 'run_experiments.py',
                    '--grid-size', '4',
                    '--iterations', '2',
                    '--interaction-steps', '2',
                    '--conductivity-method', method,
                    '--output-dir', temp_dir,
                    '--run-id', f'test_{method}'
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                assert result.returncode == 0, f"Method {method} failed: {result.stderr}"
                
                # Verify method in config
                config_path = os.path.join(temp_dir, f'test_{method}', 'config.json')
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                assert config['analysis']['conductivity_methods'] == [method]
    
    def test_output_data_format(self):
        """Test that output data follows Issue #2 specification"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '5',
                '--iterations', '3',
                '--interaction-steps', '2',
                '--output-dir', temp_dir,
                '--save-plots'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            
            run_dirs = [d for d in os.listdir(temp_dir) if d.startswith('run')]
            run_dir = os.path.join(temp_dir, run_dirs[0])
            
            # Test config.json structure
            config_path = os.path.join(run_dir, 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Verify Issue #2 config structure
            assert 'experiment' in config
            assert 'ca_parameters' in config
            assert 'simulation' in config
            assert 'analysis' in config
            assert 'computational' in config
            
            # Test metadata.json structure
            metadata_path = os.path.join(run_dir, 'metadata.json')
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            assert 'execution' in metadata
            assert 'environment' in metadata
            assert 'software' in metadata
            assert 'dependencies' in metadata
            
            # Test results_summary.csv structure
            results_path = os.path.join(run_dir, 'results_summary.csv')
            df = pd.read_csv(results_path)
            
            # Verify required columns
            required_columns = [
                'timestep', 'conductivity_simple', 'conductivity_entropy', 
                'conductivity_gradient', 'mean_activity', 'interaction_strength'
            ]
            for col in required_columns:
                assert col in df.columns, f"Required column missing: {col}"
            
            # Verify data types and ranges
            assert df['timestep'].dtype in ['int64', 'int32']
            assert all(df['conductivity_simple'] >= 0)
            assert all(df['interaction_strength'] >= 0)
    
    def test_plot_generation(self):
        """Test plot generation functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '6',
                '--iterations', '3',
                '--interaction-steps', '2',
                '--output-dir', temp_dir,
                '--save-plots'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            
            run_dirs = [d for d in os.listdir(temp_dir) if d.startswith('run')]
            plots_dir = os.path.join(temp_dir, run_dirs[0], 'plots')
            
            # Check plots directory exists
            assert os.path.exists(plots_dir), "Plots directory not created"
            
            # Check for summary plot
            summary_plot = os.path.join(plots_dir, 'summary.png')
            assert os.path.exists(summary_plot), "Summary plot not generated"
    
    def test_frame_saving(self):
        """Test grid frame saving functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '4',
                '--iterations', '3',
                '--interaction-steps', '2',
                '--output-dir', temp_dir,
                '--save-frames'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            
            run_dirs = [d for d in os.listdir(temp_dir) if d.startswith('run')]
            grids_dir = os.path.join(temp_dir, run_dirs[0], 'grids')
            
            # Check grids directory exists
            assert os.path.exists(grids_dir), "Grids directory not created"
            
            # Check for grid files
            grid_files = [f for f in os.listdir(grids_dir) if f.endswith('.npy')]
            assert len(grid_files) > 0, "No grid files saved"
            
            # Check for convenience symlinks
            initial_link = os.path.join(grids_dir, 'grid_initial.npy')
            final_link = os.path.join(grids_dir, 'grid_final.npy')
            
            # At least one should exist (symlink or copy)
            assert os.path.exists(initial_link) or os.path.exists(final_link), \
                "Convenience links not created"
    
    def test_error_handling(self):
        """Test error handling for invalid parameters"""
        # Test with invalid grid size (should handle gracefully)
        result = subprocess.run([
            'python', 'run_experiments.py',
            '--grid-size', '1',
            '--iterations', '1',
            '--interaction-steps', '1'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Should either succeed with warnings or fail gracefully
        # The key is that it shouldn't crash with unhandled exceptions
        assert result.returncode in [0, 1], "Should handle invalid parameters gracefully"
    
    def test_random_seed_reproducibility(self):
        """Test that random seed produces reproducible results"""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            # Run same experiment twice with same seed
            common_args = [
                'python', 'run_experiments.py',
                '--grid-size', '5',
                '--iterations', '3',
                '--interaction-steps', '2',
                '--random-seed', '12345'
            ]
            
            result1 = subprocess.run(
                common_args + ['--output-dir', temp_dir1],
                capture_output=True, text=True, cwd=os.getcwd()
            )
            
            result2 = subprocess.run(
                common_args + ['--output-dir', temp_dir2],
                capture_output=True, text=True, cwd=os.getcwd()
            )
            
            assert result1.returncode == 0
            assert result2.returncode == 0
            
            # Load results from both runs
            run_dirs1 = [d for d in os.listdir(temp_dir1) if d.startswith('run')]
            run_dirs2 = [d for d in os.listdir(temp_dir2) if d.startswith('run')]
            
            df1 = pd.read_csv(os.path.join(temp_dir1, run_dirs1[0], 'results_summary.csv'))
            df2 = pd.read_csv(os.path.join(temp_dir2, run_dirs2[0], 'results_summary.csv'))
            
            # Results should be identical (within numerical precision)
            pd.testing.assert_frame_equal(
                df1[['timestep', 'interaction_strength']], 
                df2[['timestep', 'interaction_strength']]
            )
            
            # Conductivity values should be very close
            assert abs(df1['conductivity_simple'].iloc[-1] - df2['conductivity_simple'].iloc[-1]) < 1e-10


class TestCLIInterface:
    """Test cases for command-line interface"""
    
    def test_argument_parsing(self):
        """Test that all required arguments are parsed correctly"""
        # This test checks if the script can parse arguments without running experiments
        result = subprocess.run([
            'python', 'run_experiments.py',
            '--grid-size', '10',
            '--iterations', '5',
            '--interaction-min', '0.1',
            '--interaction-max', '0.9',
            '--interaction-steps', '4',
            '--conductivity-method', 'entropy',
            '--random-seed', '999',
            '--help'  # Adding help to prevent actual execution
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Should show help and exit successfully
        assert result.returncode == 0
    
    def test_invalid_method_argument(self):
        """Test handling of invalid conductivity method"""
        result = subprocess.run([
            'python', 'run_experiments.py',
            '--conductivity-method', 'invalid_method'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Should fail with clear error message
        assert result.returncode != 0
        assert 'invalid choice' in result.stderr.lower() or 'error' in result.stderr.lower()


class TestAnalysisIntegration:
    """Test cases for analysis workflow integration"""
    
    def test_analysis_directory_structure(self):
        """Test that analysis directory follows Issue #2 specification"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '5',
                '--iterations', '3',
                '--interaction-steps', '2',
                '--output-dir', temp_dir
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            
            run_dirs = [d for d in os.listdir(temp_dir) if d.startswith('run')]
            run_dir = os.path.join(temp_dir, run_dirs[0])
            
            # Check directory structure
            expected_dirs = ['analysis', 'plots']
            for expected_dir in expected_dirs:
                dir_path = os.path.join(run_dir, expected_dir)
                assert os.path.exists(dir_path), f"Directory missing: {expected_dir}"
            
            # Check analysis files
            analysis_dir = os.path.join(run_dir, 'analysis')
            statistics_file = os.path.join(analysis_dir, 'statistics.json')
            assert os.path.exists(statistics_file), "Statistics file missing"
            
            # Verify statistics content
            with open(statistics_file, 'r') as f:
                stats = json.load(f)
            
            assert 'summary' in stats
            assert 'total_experiments' in stats['summary']
    
    def test_data_loading_workflow(self):
        """Test that generated data can be loaded for analysis"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'python', 'run_experiments.py',
                '--grid-size', '5',
                '--iterations', '4',
                '--interaction-steps', '3',
                '--output-dir', temp_dir
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            
            run_dirs = [d for d in os.listdir(temp_dir) if d.startswith('run')]
            run_dir = os.path.join(temp_dir, run_dirs[0])
            
            # Test data loading as would be done in analysis
            results_path = os.path.join(run_dir, 'results_summary.csv')
            config_path = os.path.join(run_dir, 'config.json')
            
            # Load and validate data
            df = pd.read_csv(results_path)
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Verify data consistency
            expected_experiments = len(config['ca_parameters']['interaction_values'])
            expected_iterations = config['simulation']['iterations']
            expected_total_rows = expected_experiments * (expected_iterations + 1)  # +1 for initial state
            
            assert len(df) == expected_total_rows, \
                f"Expected {expected_total_rows} rows, got {len(df)}"
            
            # Verify conductivity calculations are reasonable
            assert all(df['conductivity_simple'] >= 0), "Negative conductivity values found"
            assert all(df['conductivity_entropy'] >= 0), "Negative entropy conductivity values found"
            
            # Test basic analysis operations
            mean_conductivity = df.groupby('interaction_strength')['conductivity_simple'].mean()
            assert len(mean_conductivity) == expected_experiments, \
                "Incorrect number of interaction strength groups"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
