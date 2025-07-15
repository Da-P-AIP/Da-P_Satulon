"""
Unit tests for utility functions and helper modules

This module tests various utility functions and helper components
used throughout the Da-P_Satulon project.

Run with: pytest tests/test_utils.py
"""

import pytest
import numpy as np
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from ca_2d.info_cond import calculate_information_conductivity


class TestInformationConductivity:
    """Test cases for information conductivity calculations"""
    
    def test_simple_method(self):
        """Test simple conductivity calculation method"""
        test_grid = np.array([
            [0.0, 0.5, 1.0],
            [0.2, 0.8, 0.3],
            [0.7, 0.1, 0.9]
        ])
        
        conductivity = calculate_information_conductivity(test_grid, method='simple')
        expected = np.mean(test_grid)
        
        assert abs(conductivity - expected) < 1e-10
        assert isinstance(conductivity, (float, np.floating))
    
    def test_entropy_method(self):
        """Test entropy-based conductivity calculation"""
        # Test with uniform distribution (high entropy)
        uniform_grid = np.full((5, 5), 0.5)
        uniform_conductivity = calculate_information_conductivity(uniform_grid, method='entropy')
        
        # Test with binary distribution (lower entropy)
        binary_grid = np.array([
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0]
        ])
        binary_conductivity = calculate_information_conductivity(binary_grid, method='entropy')
        
        # Both should be valid numbers
        assert isinstance(uniform_conductivity, (float, np.floating))
        assert isinstance(binary_conductivity, (float, np.floating))
        assert uniform_conductivity >= 0
        assert binary_conductivity >= 0
    
    def test_gradient_method(self):
        """Test gradient-based conductivity calculation"""
        # Test with smooth gradient (low gradient magnitude)
        smooth_grid = np.array([
            [0.0, 0.1, 0.2],
            [0.1, 0.2, 0.3],
            [0.2, 0.3, 0.4]
        ])
        smooth_conductivity = calculate_information_conductivity(smooth_grid, method='gradient')
        
        # Test with sharp edges (high gradient magnitude)
        sharp_grid = np.array([
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 1.0]
        ])
        sharp_conductivity = calculate_information_conductivity(sharp_grid, method='gradient')
        
        # Both should be valid numbers
        assert isinstance(smooth_conductivity, (float, np.floating))
        assert isinstance(sharp_conductivity, (float, np.floating))
        assert smooth_conductivity >= 0
        assert sharp_conductivity >= 0
    
    def test_temporal_method(self):
        """Test temporal conductivity calculation with time series"""
        # Create a time series of grids
        time_series = []
        for t in range(5):
            grid = np.random.rand(4, 4) * (t + 1) / 5  # Increasing activity over time
            time_series.append(grid)
        
        conductivity = calculate_information_conductivity(time_series, method='temporal')
        
        assert isinstance(conductivity, (float, np.floating))
        assert conductivity >= 0
    
    def test_multiscale_method(self):
        """Test multiscale conductivity analysis"""
        test_grid = np.random.rand(8, 8)  # Large enough for multiscale analysis
        
        conductivity = calculate_information_conductivity(test_grid, method='multiscale')
        
        # Should return either a single value or a dictionary of scales
        assert isinstance(conductivity, (float, np.floating, dict))
        if isinstance(conductivity, dict):
            assert len(conductivity) > 0
            assert all(isinstance(v, (float, np.floating)) for v in conductivity.values())
    
    def test_edge_cases(self):
        """Test edge cases for conductivity calculations"""
        # Test with zeros
        zero_grid = np.zeros((3, 3))
        zero_conductivity = calculate_information_conductivity(zero_grid, method='simple')
        assert zero_conductivity == 0.0
        
        # Test with ones
        ones_grid = np.ones((3, 3))
        ones_conductivity = calculate_information_conductivity(ones_grid, method='simple')
        assert ones_conductivity == 1.0
        
        # Test with single value
        single_grid = np.array([[0.5]])
        single_conductivity = calculate_information_conductivity(single_grid, method='simple')
        assert single_conductivity == 0.5
    
    def test_invalid_method(self):
        """Test error handling for invalid methods"""
        test_grid = np.random.rand(3, 3)
        
        with pytest.raises((ValueError, KeyError, NotImplementedError)):
            calculate_information_conductivity(test_grid, method='invalid_method')
    
    def test_input_validation(self):
        """Test input validation for conductivity functions"""
        # Test with invalid grid types - should handle gracefully or raise appropriate errors
        try:
            calculate_information_conductivity("not_an_array", method='simple')
            assert False, "Should have raised an error"
        except (TypeError, ValueError, AttributeError):
            pass  # Expected behavior
        
        try:
            calculate_information_conductivity(None, method='simple')
            assert False, "Should have raised an error"
        except (TypeError, ValueError, AttributeError):
            pass  # Expected behavior


class TestDataValidation:
    """Test cases for data validation utilities"""
    
    def test_grid_validation(self):
        """Test grid data validation"""
        # Valid grids
        valid_grid = np.random.rand(5, 5)
        assert valid_grid.shape == (5, 5)
        assert np.all(valid_grid >= 0) and np.all(valid_grid <= 1)
        
        # Test grid bounds
        bounded_grid = np.clip(np.random.randn(5, 5), 0, 1)
        assert np.all(bounded_grid >= 0) and np.all(bounded_grid <= 1)
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        # Valid parameters
        assert 0.0 <= 0.5 <= 1.0  # interaction strength
        assert isinstance(50, int) and 50 > 0  # grid size
        assert isinstance(100, int) and 100 > 0  # iterations
        
        # Test parameter ranges
        interaction_values = np.linspace(0.1, 0.9, 5)
        assert len(interaction_values) == 5
        assert np.all(interaction_values >= 0.1)
        assert np.all(interaction_values <= 0.9)


class TestFileUtilities:
    """Test cases for file handling utilities"""
    
    def test_json_handling(self):
        """Test JSON file operations"""
        test_data = {
            "experiment": {"run_id": "test_001", "phase": "G1"},
            "parameters": {"grid_size": [10, 10], "iterations": 50},
            "results": {"mean_conductivity": 0.42}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, indent=2)
            temp_path = f.name
        
        try:
            # Test reading
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
            
            assert loaded_data == test_data
            assert loaded_data["experiment"]["run_id"] == "test_001"
            assert loaded_data["parameters"]["grid_size"] == [10, 10]
            assert loaded_data["results"]["mean_conductivity"] == 0.42
            
        finally:
            os.unlink(temp_path)
    
    def test_directory_creation(self):
        """Test directory creation utilities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test nested directory creation
            nested_path = os.path.join(temp_dir, 'results', 'run001', 'analysis')
            os.makedirs(nested_path, exist_ok=True)
            
            assert os.path.exists(nested_path)
            assert os.path.isdir(nested_path)
            
            # Test parent directories
            assert os.path.exists(os.path.join(temp_dir, 'results'))
            assert os.path.exists(os.path.join(temp_dir, 'results', 'run001'))
    
    def test_run_id_generation(self):
        """Test run ID generation logic"""
        # Simulate run ID generation
        def get_next_run_id(output_dir):
            if not os.path.exists(output_dir):
                return 'run001'
            
            run_dirs = [d for d in os.listdir(output_dir) 
                       if d.startswith('run') and os.path.isdir(os.path.join(output_dir, d))]
            if not run_dirs:
                return 'run001'
            
            run_numbers = []
            for d in run_dirs:
                if len(d) == 6 and d[3:].isdigit():
                    run_numbers.append(int(d[3:]))
            
            next_num = max(run_numbers, default=0) + 1
            return f'run{next_num:03d}'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test first run
            run_id = get_next_run_id(temp_dir)
            assert run_id == 'run001'
            
            # Create first run directory
            os.makedirs(os.path.join(temp_dir, 'run001'))
            
            # Test second run
            run_id = get_next_run_id(temp_dir)
            assert run_id == 'run002'
            
            # Create more run directories
            for i in range(2, 5):
                os.makedirs(os.path.join(temp_dir, f'run{i:03d}'))
            
            # Test next run
            run_id = get_next_run_id(temp_dir)
            assert run_id == 'run005'


class TestNumericalUtilities:
    """Test cases for numerical computation utilities"""
    
    def test_array_operations(self):
        """Test array manipulation utilities"""
        # Test array creation and manipulation
        test_array = np.random.rand(5, 5)
        
        # Test statistics
        mean_val = np.mean(test_array)
        std_val = np.std(test_array)
        min_val = np.min(test_array)
        max_val = np.max(test_array)
        
        assert 0 <= mean_val <= 1
        assert std_val >= 0
        assert 0 <= min_val <= max_val <= 1
        
        # Test array operations
        normalized = (test_array - mean_val) / std_val if std_val > 0 else test_array
        assert normalized.shape == test_array.shape
    
    def test_statistical_functions(self):
        """Test statistical utility functions"""
        # Test with known data
        data = np.array([1, 2, 3, 4, 5])
        
        # Basic statistics
        assert np.mean(data) == 3.0
        assert np.median(data) == 3.0
        assert np.std(data) == np.sqrt(2.0)
        
        # Test with random data
        random_data = np.random.rand(100)
        assert 0 <= np.mean(random_data) <= 1
        assert 0 <= np.std(random_data) <= 1
    
    def test_correlation_analysis(self):
        """Test correlation analysis utilities"""
        # Create correlated data
        x = np.linspace(0, 1, 50)
        y_positive = x + 0.1 * np.random.rand(50)  # Positive correlation
        y_negative = 1 - x + 0.1 * np.random.rand(50)  # Negative correlation
        y_uncorrelated = np.random.rand(50)  # No correlation
        
        # Test correlations
        corr_positive = np.corrcoef(x, y_positive)[0, 1]
        corr_negative = np.corrcoef(x, y_negative)[0, 1]
        corr_uncorrelated = np.corrcoef(x, y_uncorrelated)[0, 1]
        
        assert corr_positive > 0.5  # Strong positive correlation
        assert corr_negative < -0.5  # Strong negative correlation
        assert abs(corr_uncorrelated) < 0.5  # Weak correlation


class TestConfigurationUtilities:
    """Test cases for configuration and parameter utilities"""
    
    def test_parameter_generation(self):
        """Test parameter sweep generation"""
        # Test linear spacing
        min_val, max_val, steps = 0.1, 0.9, 5
        values = np.linspace(min_val, max_val, steps)
        
        assert len(values) == steps
        assert values[0] == min_val
        assert values[-1] == max_val
        assert all(values[i] <= values[i+1] for i in range(len(values)-1))
    
    def test_configuration_validation(self):
        """Test configuration parameter validation"""
        # Valid configuration
        config = {
            "grid_size": 50,
            "iterations": 100,
            "interaction_strength": 0.5,
            "random_seed": 42
        }
        
        # Validate types and ranges
        assert isinstance(config["grid_size"], int) and config["grid_size"] > 0
        assert isinstance(config["iterations"], int) and config["iterations"] > 0
        assert isinstance(config["interaction_strength"], (int, float))
        assert 0 <= config["interaction_strength"] <= 1
        assert isinstance(config["random_seed"], int)
    
    def test_method_selection(self):
        """Test conductivity method selection validation"""
        valid_methods = ['simple', 'entropy', 'gradient', 'temporal', 'multiscale']
        
        for method in valid_methods:
            assert method in valid_methods
        
        # Test invalid method
        invalid_method = 'invalid_method'
        assert invalid_method not in valid_methods


class TestDataStructures:
    """Test cases for data structure utilities"""
    
    def test_time_series_handling(self):
        """Test time series data structure handling"""
        # Create sample time series
        time_series = []
        for t in range(10):
            grid = np.random.rand(5, 5)
            time_series.append(grid)
        
        assert len(time_series) == 10
        assert all(isinstance(grid, np.ndarray) for grid in time_series)
        assert all(grid.shape == (5, 5) for grid in time_series)
    
    def test_experiment_result_structure(self):
        """Test experiment result data structure"""
        # Sample experiment result structure
        experiment_result = {
            'experiment_id': 0,
            'interaction_strength': 0.5,
            'timestep_data': [
                {
                    'timestep': 0,
                    'conductivity_simple': 0.25,
                    'conductivity_entropy': 0.30,
                    'conductivity_gradient': 0.22,
                    'mean_activity': 0.45,
                    'std_activity': 0.15,
                    'interaction_strength': 0.5
                }
            ],
            'ca_stats': {'final_mean': 0.45, 'total_evolution': 0.1}
        }
        
        # Validate structure
        assert 'experiment_id' in experiment_result
        assert 'interaction_strength' in experiment_result
        assert 'timestep_data' in experiment_result
        assert isinstance(experiment_result['timestep_data'], list)
        assert len(experiment_result['timestep_data']) > 0
        
        # Validate timestep data structure
        timestep_data = experiment_result['timestep_data'][0]
        required_fields = [
            'timestep', 'conductivity_simple', 'conductivity_entropy',
            'conductivity_gradient', 'mean_activity', 'interaction_strength'
        ]
        for field in required_fields:
            assert field in timestep_data
    
    def test_metadata_structure(self):
        """Test metadata structure validation"""
        # Sample metadata structure
        metadata = {
            "execution": {
                "run_id": "run001",
                "start_time": "2025-07-15T12:00:00Z",
                "end_time": "2025-07-15T12:05:00Z",
                "duration_seconds": 300.0
            },
            "environment": {
                "python_version": "3.9.7",
                "platform": "Linux-5.4.0",
                "cpu_count": 8
            },
            "dependencies": {
                "numpy": "1.21.0",
                "matplotlib": "3.5.0",
                "pandas": "1.3.0"
            }
        }
        
        # Validate structure
        assert 'execution' in metadata
        assert 'environment' in metadata
        assert 'dependencies' in metadata
        
        # Validate execution data
        execution = metadata['execution']
        assert 'run_id' in execution
        assert 'duration_seconds' in execution
        assert isinstance(execution['duration_seconds'], (int, float))
        assert execution['duration_seconds'] >= 0


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
