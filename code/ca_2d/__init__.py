"""
Da-P_Satulon CA-2D Module

This module provides the core functionality for 2D Cellular Automata 
with Information Conductivity analysis.

Author: Da-P-AIP Research Team
Version: 0.1.0 (G1 Phase)
"""

from .grid import CA2D

# Expose key functions for easy import
__version__ = "0.1.0"
__author__ = "Da-P-AIP Research Team"

# Main exports
__all__ = [
    "CA2D",
    "information_conductivity_stub", 
]


def information_conductivity_stub(grid_state):
    """
    Stub implementation of information conductivity calculation
    
    This is a placeholder function that will be replaced with proper
    information theory metrics in future development phases.
    
    Args:
        grid_state (np.ndarray): 2D grid state
        
    Returns:
        float: Information conductivity measure (currently grid mean)
    """
    import numpy as np
    return float(np.mean(grid_state))


# Convenience function for quick CA creation
def create_ca(grid_size=50, interaction_strength=0.5, seed=None):
    """
    Convenience function to create a CA2D instance
    
    Args:
        grid_size (int): Size of square grid (default: 50)
        interaction_strength (float): Interaction strength (default: 0.5)
        seed (int): Random seed for reproducibility (default: None)
        
    Returns:
        CA2D: Initialized cellular automaton instance
    """
    return CA2D(
        grid_size=(grid_size, grid_size),
        interaction_strength=interaction_strength,
        random_seed=seed
    )


# Add to exports
__all__.append("create_ca")
