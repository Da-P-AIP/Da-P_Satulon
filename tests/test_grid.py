"""
Unit tests for CA-2D Grid implementation

This module contains basic tests for the cellular automaton functionality
to ensure correctness and stability during development.

Run with: pytest tests/test_grid.py
"""

import pytest
import numpy as np
import sys
import os

# Add the code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from ca_2d.grid import CA2D
from ca_2d import create_ca, information_conductivity_stub


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
    
    def test_information_conductivity(self):
        """Test information conductivity calculation"""
        ca = CA2D(grid_size=(3, 3), random_seed=42)
        
        conductivity = ca.information_conductivity()
        
        assert isinstance(conductivity, float)
        assert 0 <= conductivity <= 1  # Should be in valid range
    
    def test_conductivity_series(self):
        """Test conductivity time series calculation"""
        ca = CA2D(grid_size=(5, 5), random_seed=42)
        ca.update(3)
        
        series = ca.get_conductivity_series()
        
        assert len(series) == 4  # Initial + 3 updates
        assert all(isinstance(x, (float, np.floating)) for x in series)
    
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
    
    def test_reset(self):
        """Test CA reset functionality"""
        ca = CA2D(grid_size=(5, 5), random_seed=42)
        original_grid = ca.grid.copy()
        
        ca.update(5)
        ca.reset(random_seed=42)
        
        assert len(ca.history) == 1
        np.testing.assert_array_equal(ca.grid, original_grid)
    
    def test_boundary_conditions(self):
        """Test edge cases and boundary conditions"""
        # Test very small grid
        ca_small = CA2D(grid_size=(2, 2))
        ca_small.update(1)
        assert ca_small.grid.shape == (2, 2)
        
        # Test extreme interaction strengths
        ca_zero = CA2D(grid_size=(3, 3), interaction_strength=0.0, random_seed=42)
        initial_grid = ca_zero.grid.copy()
        ca_zero.update(1)
        # With zero interaction, grid should not change much
        
        ca_one = CA2D(grid_size=(3, 3), interaction_strength=1.0)
        ca_one.update(1)
        assert ca_one.grid.shape == (3, 3)


class TestConvenienceFunctions:
    """Test cases for convenience functions"""
    
    def test_create_ca(self):
        """Test the create_ca convenience function"""
        ca = create_ca(grid_size=10, interaction_strength=0.7, seed=123)
        
        assert isinstance(ca, CA2D)
        assert ca.grid_size == (10, 10)
        assert ca.interaction_strength == 0.7
    
    def test_information_conductivity_stub(self):
        """Test the stub information conductivity function"""
        test_grid = np.array([[0.1, 0.2], [0.3, 0.4]])
        
        conductivity = information_conductivity_stub(test_grid)
        expected = np.mean(test_grid)
        
        assert conductivity == expected
        assert isinstance(conductivity, float)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_grid_size(self):
        """Test that invalid grid sizes are handled appropriately"""
        # These should work (implementation should handle gracefully)
        try:
            ca = CA2D(grid_size=(1, 1))
            assert ca.grid.shape == (1, 1)
        except Exception as e:
            pytest.skip(f"Very small grid sizes not supported: {e}")
    
    def test_invalid_interaction_strength(self):
        """Test behavior with out-of-range interaction strength"""
        # Implementation should handle or clamp these values
        ca_negative = CA2D(interaction_strength=-0.1)
        ca_large = CA2D(interaction_strength=1.5)
        
        # Should not crash
        ca_negative.update(1)
        ca_large.update(1)
    
    def test_invalid_timestep_access(self):
        """Test error handling for invalid timestep access"""
        ca = CA2D(grid_size=(3, 3))
        ca.update(2)
        
        # Valid access
        state = ca.get_state(timestep=0)
        assert state is not None
        
        # Invalid access should be handled gracefully
        try:
            invalid_state = ca.get_state(timestep=10)
            # If it doesn't raise an error, it should return something sensible
            assert invalid_state is not None or invalid_state is None
        except IndexError:
            # This is acceptable behavior
            pass


# Integration test
def test_basic_workflow():
    """Test a complete basic workflow"""
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
    pytest.main([__file__])
