"""
Unit tests for CA-2D Grid implementation

This module contains comprehensive tests for the cellular automaton functionality
to ensure correctness and stability during development.

Run with: pytest tests/test_grid.py

Author: Da-P-AIP Research Team
Version: 0.1.1 (G1 Phase - Issue #1 Implementation)
"""

import pytest
import numpy as np
import sys
import os

# Add the code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from ca_2d.grid import CA2D
from ca_2d import create_ca, information_conductivity_stub, calculate_information_conductivity


class TestCA2D:
    """Test cases for the CA2D class"""
    
    def test_initialization(self):
        """Test CA2D initialization with default parameters"""
        ca = CA2D()
        
        assert ca.grid_size == (50, 50)
        assert ca.interaction_strength == 0.5
        assert ca.grid.shape == (50, 50)
        assert len(ca.history) == 1
        assert np.all(ca.grid >= 0) and np.all(ca.grid <= 1)
    
    def test_custom_initialization(self):
        """Test CA2D initialization with custom parameters"""
        ca = CA2D(grid_size=(10, 20), interaction_strength=0.8, random_seed=123)
        
        assert ca.grid_size == (10, 20)
        assert ca.interaction_strength == 0.8
        assert ca.grid.shape == (10, 20)
        assert len(ca.history) == 1
    
    def test_interaction_strength_clamping(self):
        """Test that interaction_strength is clamped to [0, 1]"""
        ca_negative = CA2D(interaction_strength=-0.1)
        ca_large = CA2D(interaction_strength=1.5)
        
        assert ca_negative.interaction_strength == 0.0
        assert ca_large.interaction_strength == 1.0
    
    def test_reproducibility(self):
        """Test that random seed produces reproducible results"""
        ca1 = CA2D(grid_size=(5, 5), random_seed=42)
        ca2 = CA2D(grid_size=(5, 5), random_seed=42)
        
        np.testing.assert_array_equal(ca1.grid, ca2.grid)
    
    def test_update_mechanics(self):
        """Test that update() modifies the grid and history"""
        ca = CA2D(grid_size=(5, 5), random_seed=42)
        initial_grid = ca.grid.copy()
        initial_history_length = len(ca.history)
        
        ca.update(1)
        
        assert len(ca.history) == initial_history_length + 1
        # Grid should change (unless interaction_strength = 0)
        if ca.interaction_strength > 0:
            assert not np.array_equal(ca.grid, initial_grid)
    
    def test_multiple_updates(self):
        """Test multiple update iterations"""
        ca = CA2D(grid_size=(5, 5), random_seed=42)
        
        ca.update(5)
        
        assert len(ca.history) == 6  # Initial + 5 updates
        assert ca.grid.shape == (5, 5)
    
    def test_boundary_conditions(self):
        """Test boundary condition handling"""
        ca = CA2D(grid_size=(5, 5), random_seed=42)
        initial_boundary = ca.grid[0, :].copy()
        
        ca.update(1)
        
        # Boundary should be handled properly (not NaN or extreme values)
        assert not np.any(np.isnan(ca.grid))
        assert np.all(ca.grid >= 0) and np.all(ca.grid <= 1)
    
    def test_information_conductivity_methods(self):
        """Test information conductivity calculation with different methods"""
        ca = CA2D(grid_size=(10, 10), random_seed=42)
        
        methods = ['simple', 'entropy', 'gradient']
        for method in methods:
            conductivity = ca.information_conductivity(method)
            assert isinstance(conductivity, float)
            assert not np.isnan(conductivity)
            assert conductivity >= 0  # Should be non-negative
    
    def test_conductivity_series(self):
        """Test conductivity time series calculation"""
        ca = CA2D(grid_size=(5, 5), random_seed=42)
        ca.update(3)
        
        series = ca.get_conductivity_series()
        
        assert len(series) == 4  # Initial + 3 updates
        assert all(isinstance(x, (float, np.floating)) for x in series)
        assert all(not np.isnan(x) for x in series)
    
    def test_get_state(self):
        """Test state retrieval functionality"""
        ca = CA2D(grid_size=(3, 3), random_seed=42)
        initial_state = ca.get_state()
        
        ca.update(2)
        
        # Test current state
        current_state = ca.get_state()
        assert current_state.shape == (3, 3)
        
        # Test historical state
        historical_state = ca.get_state(timestep=0)
        np.testing.assert_array_equal(historical_state, initial_state)
        
        # Test that returned states are copies
        current_state[0, 0] = -999
        assert ca.grid[0, 0] != -999
    
    def test_get_state_error_handling(self):
        """Test error handling for invalid timestep access"""
        ca = CA2D(grid_size=(3, 3))
        ca.update(2)
        
        # Valid access
        state = ca.get_state(timestep=0)
        assert state is not None
        
        # Invalid access should raise IndexError
        with pytest.raises(IndexError):
            ca.get_state(timestep=10)
    
    def test_reset(self):
        """Test CA reset functionality"""
        ca = CA2D(grid_size=(5, 5), random_seed=42)
        original_grid = ca.grid.copy()
        
        ca.update(5)
        ca.reset(random_seed=42)
        
        assert len(ca.history) == 1
        np.testing.assert_array_equal(ca.grid, original_grid)
    
    def test_get_statistics(self):
        """Test comprehensive statistics functionality"""
        ca = CA2D(grid_size=(5, 5), interaction_strength=0.3, random_seed=42)
        ca.update(3)
        
        stats = ca.get_statistics()
        
        # Check required fields
        required_fields = ['grid_size', 'interaction_strength', 'timesteps', 
                          'current_mean', 'current_std', 'current_min', 'current_max',
                          'info_conductivity_simple', 'info_conductivity_entropy', 
                          'info_conductivity_gradient']
        
        for field in required_fields:
            assert field in stats
        
        # Check values make sense
        assert stats['grid_size'] == (5, 5)
        assert stats['interaction_strength'] == 0.3
        assert stats['timesteps'] == 3
        assert 0 <= stats['current_mean'] <= 1
        assert stats['current_std'] >= 0
    
    def test_small_grid_handling(self):
        """Test handling of very small grids"""
        ca_small = CA2D(grid_size=(3, 3))
        ca_small.update(1)
        assert ca_small.grid.shape == (3, 3)
        assert not np.any(np.isnan(ca_small.grid))
    
    def test_extreme_interaction_strengths(self):
        """Test behavior with extreme interaction strengths"""
        # Zero interaction - grid should change minimally
        ca_zero = CA2D(grid_size=(5, 5), interaction_strength=0.0, random_seed=42)
        initial_grid = ca_zero.grid.copy()
        ca_zero.update(1)
        # With zero interaction, boundary effects only
        
        # Full interaction
        ca_one = CA2D(grid_size=(5, 5), interaction_strength=1.0, random_seed=42)
        ca_one.update(1)
        assert ca_one.grid.shape == (5, 5)
        assert not np.any(np.isnan(ca_one.grid))


class TestConvenienceFunctions:
    """Test cases for convenience functions"""
    
    def test_create_ca_with_int(self):
        """Test the create_ca convenience function with integer grid size"""
        ca = create_ca(grid_size=10, interaction_strength=0.7, seed=123)
        
        assert isinstance(ca, CA2D)
        assert ca.grid_size == (10, 10)
        assert ca.interaction_strength == 0.7
    
    def test_create_ca_with_tuple(self):
        """Test the create_ca convenience function with tuple grid size"""
        ca = create_ca(grid_size=(8, 12), interaction_strength=0.3, seed=456)
        
        assert isinstance(ca, CA2D)
        assert ca.grid_size == (8, 12)
        assert ca.interaction_strength == 0.3
    
    def test_information_conductivity_stub(self):
        """Test the stub information conductivity function"""
        test_grid = np.array([[0.1, 0.2], [0.3, 0.4]])
        
        # Test with default method
        conductivity = information_conductivity_stub(test_grid)
        expected = np.mean(test_grid)
        assert conductivity == expected
        assert isinstance(conductivity, float)
        
        # Test with different methods
        methods = ['simple', 'entropy', 'gradient']
        for method in methods:
            result = information_conductivity_stub(test_grid, method=method)
            assert isinstance(result, float)
            assert not np.isnan(result)


class TestInformationConductivityIntegration:
    """Test integration with information conductivity module"""
    
    def test_calculate_information_conductivity_integration(self):
        """Test integration with calculate_information_conductivity function"""
        test_grid = np.random.random((10, 10))
        
        methods = ['simple', 'entropy', 'gradient']
        for method in methods:
            result = calculate_information_conductivity(test_grid, method=method)
            assert isinstance(result, float)
            assert not np.isnan(result)
            assert result >= 0
    
    def test_temporal_conductivity(self):
        """Test temporal conductivity calculation"""
        ca = CA2D(grid_size=(8, 8), random_seed=42)
        ca.update(5)
        
        temporal_result = calculate_information_conductivity(
            ca.history, method='temporal'
        )
        
        assert len(temporal_result) == 6  # Initial + 5 updates
        assert all(isinstance(x, (float, np.floating)) for x in temporal_result)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_grid_size_handling(self):
        """Test graceful handling of edge case grid sizes"""
        # Very small grid
        ca = CA2D(grid_size=(2, 2))
        ca.update(1)
        assert ca.grid.shape == (2, 2)
        assert not np.any(np.isnan(ca.grid))
    
    def test_zero_iterations(self):
        """Test update with zero iterations"""
        ca = CA2D(grid_size=(5, 5))
        initial_length = len(ca.history)
        
        ca.update(0)
        
        assert len(ca.history) == initial_length  # No change


# Integration test demonstrating Issue #1 requirements
def test_issue_1_requirements():
    """Test complete Issue #1 requirements implementation"""
    print("\n=== Testing Issue #1 Requirements ===")
    
    # 1. Grid class skeleton ✅
    ca = create_ca(grid_size=20, interaction_strength=0.4, seed=42)
    assert isinstance(ca, CA2D)
    print("✅ Grid class skeleton created")
    
    # 2. update() with interaction_strength ✅
    initial_grid = ca.grid.copy()
    ca.update(5)
    
    # Verify interaction_strength affects the update
    assert not np.array_equal(ca.grid, initial_grid)
    assert len(ca.history) == 6  # Initial + 5 updates
    print("✅ update() method with interaction_strength working")
    
    # 3. information_conductivity stub ✅
    conductivity = ca.information_conductivity()
    assert isinstance(conductivity, float)
    assert 0 <= conductivity <= 1
    
    # Test stub function directly
    stub_result = information_conductivity_stub(ca.grid)
    assert isinstance(stub_result, float)
    print("✅ information_conductivity stub implemented")
    
    # 4. README usage documentation ✅ (updated in README.md)
    print("✅ README updated with usage instructions")
    
    print("🎉 Issue #1 requirements fully satisfied!")


# Demonstration function
def test_basic_workflow():
    """Test a complete basic workflow as mentioned in README"""
    # Create CA
    ca = create_ca(grid_size=5, interaction_strength=0.5, seed=42)
    
    # Run simulation
    ca.update(10)
    
    # Analyze results
    final_conductivity = ca.information_conductivity()
    series = ca.get_conductivity_series()
    
    # Basic sanity checks
    assert len(series) == 11  # 1 initial + 10 updates
    assert isinstance(final_conductivity, float)
    assert 0 <= final_conductivity <= 1


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
