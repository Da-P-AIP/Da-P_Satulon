"""
Da-P_Satulon CA-2D Module

This module provides the core functionality for 2D Cellular Automata 
with Information Conductivity analysis.

Author: Da-P-AIP Research Team
Version: 0.1.1 (G1 Phase - Issue #1 Implementation)
"""

from .grid import CA2D
from .info_cond import calculate_information_conductivity

# Expose key functions for easy import
__version__ = "0.1.1"
__author__ = "Da-P-AIP Research Team"

# Main exports
__all__ = [
    "CA2D",
    "information_conductivity_stub", 
    "calculate_information_conductivity",
    "create_ca",
]


def information_conductivity_stub(grid_state, method='simple'):
    """
    Improved stub implementation of information conductivity calculation
    
    This function now delegates to the comprehensive info_cond module
    while maintaining backward compatibility.
    
    Args:
        grid_state (np.ndarray): 2D grid state
        method (str): Calculation method ('simple', 'entropy', 'gradient')
        
    Returns:
        float: Information conductivity measure
    """
    return calculate_information_conductivity(grid_state, method=method)


# Convenience function for quick CA creation
def create_ca(grid_size=50, interaction_strength=0.5, seed=None):
    """
    Convenience function to create a CA2D instance
    
    Args:
        grid_size (int or tuple): Size of grid (default: 50)
                                 If int, creates square grid
                                 If tuple, uses (height, width)
        interaction_strength (float): Interaction strength (default: 0.5)
        seed (int): Random seed for reproducibility (default: None)
        
    Returns:
        CA2D: Initialized cellular automaton instance
    """
    if isinstance(grid_size, int):
        grid_size = (grid_size, grid_size)
    
    return CA2D(
        grid_size=grid_size,
        interaction_strength=interaction_strength,
        random_seed=seed
    )


# Demonstration function for Issue #1 requirements
def demo_ca_functionality():
    """
    Demonstration of CA-2D functionality as required by Issue #1
    
    This function showcases:
    - CA2D class creation
    - update() with interaction_strength
    - information_conductivity calculation with stub
    """
    print("=== DA-P_Satulon CA-2D Demo (Issue #1) ===")
    
    # Create CA instance
    ca = create_ca(grid_size=20, interaction_strength=0.4, seed=42)
    print(f"Created CA: {ca.grid_size} grid, interaction_strength={ca.interaction_strength}")
    
    # Test initial state
    initial_conductivity = ca.information_conductivity()
    print(f"Initial conductivity: {initial_conductivity:.4f}")
    
    # Run updates
    print("Running 5 update iterations...")
    ca.update(5)
    
    # Test final state with multiple methods
    methods = ['simple', 'entropy', 'gradient']
    print("Final conductivity by method:")
    for method in methods:
        conductivity = ca.information_conductivity(method)
        print(f"  {method}: {conductivity:.4f}")
    
    # Test stub function directly
    stub_result = information_conductivity_stub(ca.grid)
    print(f"Stub function result: {stub_result:.4f}")
    
    # Display statistics
    stats = ca.get_statistics()
    print(f"System evolved over {stats['timesteps']} timesteps")
    print(f"Current grid statistics: mean={stats['current_mean']:.3f}, std={stats['current_std']:.3f}")
    
    print("=== Demo Complete ===")
    return ca


if __name__ == "__main__":
    # Run demo when module is executed directly
    demo_ca_functionality()
