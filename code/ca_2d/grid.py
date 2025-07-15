"""
2D Cellular Automata with Information Conductivity

This module implements the core CA-2D class for studying information 
conductivity in 2D cellular automata systems.

Author: Da-P-AIP Research Team
Version: 0.1.1 (G1 Phase - Issue #1 Implementation)
"""

import numpy as np
from typing import Tuple, Optional
from .info_cond import calculate_information_conductivity


class CA2D:
    """2D Cellular Automata with Information Conductivity Analysis
    
    This class provides the core functionality for simulating 2D cellular
    automata and calculating information conductivity metrics.
    
    Attributes:
        grid_size (Tuple[int, int]): Height and width of the grid
        interaction_strength (float): Strength of cell interactions
        grid (np.ndarray): Current state of the cellular automaton
        history (list): History of grid states for analysis
    """
    
    def __init__(self, 
                 grid_size: Tuple[int, int] = (50, 50),
                 interaction_strength: float = 0.5,
                 random_seed: Optional[int] = None):
        """Initialize the 2D Cellular Automaton
        
        Args:
            grid_size: (height, width) of the grid
            interaction_strength: Strength of neighbor interactions [0, 1]
            random_seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.interaction_strength = max(0.0, min(1.0, interaction_strength))  # Clamp to [0,1]
        self.history = []
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize grid with random values
        self.grid = np.random.random(grid_size)
        self.history.append(self.grid.copy())
    
    def update(self, iterations: int = 1) -> None:
        """Update the cellular automaton for specified iterations
        
        Args:
            iterations: Number of update steps to perform
        """
        for _ in range(iterations):
            self._single_update()
            self.history.append(self.grid.copy())
    
    def _single_update(self) -> None:
        """Perform a single update step of the cellular automaton
        
        Implements a diffusion-like cellular automaton with configurable
        interaction strength.
        """
        h, w = self.grid_size
        new_grid = self.grid.copy()
        
        # Apply CA rules with interaction_strength
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                # Calculate neighbor influence
                neighbors = (self.grid[i-1, j] + self.grid[i+1, j] + 
                           self.grid[i, j-1] + self.grid[i, j+1])
                neighbor_avg = neighbors / 4.0
                
                # Update rule: blend current state with neighbor average
                # interaction_strength=0: no change
                # interaction_strength=1: full neighbor averaging
                new_grid[i, j] = (self.grid[i, j] * (1 - self.interaction_strength) + 
                                neighbor_avg * self.interaction_strength)
        
        # Handle boundary conditions (periodic or zero-flux)
        self._apply_boundary_conditions(new_grid)
        
        self.grid = new_grid
    
    def _apply_boundary_conditions(self, grid: np.ndarray) -> None:
        """Apply boundary conditions to the grid
        
        Args:
            grid: Grid to apply boundary conditions to (modified in-place)
        """
        h, w = self.grid_size
        
        # Zero-flux boundary conditions (no change at boundaries)
        # Alternative: could implement periodic or other boundary conditions
        
        # Top and bottom rows
        grid[0, :] = grid[1, :]
        grid[h-1, :] = grid[h-2, :]
        
        # Left and right columns  
        grid[:, 0] = grid[:, 1]
        grid[:, w-1] = grid[:, w-2]
    
    def information_conductivity(self, method: str = 'simple') -> float:
        """Calculate information conductivity of current grid state
        
        Args:
            method: Calculation method ('simple', 'entropy', 'gradient')
        
        Returns:
            float: Information conductivity measure
        """
        return calculate_information_conductivity(
            self.grid, 
            method=method,
            interaction_strength=self.interaction_strength
        )
    
    def get_conductivity_series(self, method: str = 'simple') -> np.ndarray:
        """Calculate information conductivity for all states in history
        
        Args:
            method: Calculation method ('simple', 'entropy', 'gradient')
        
        Returns:
            np.ndarray: Time series of conductivity values
        """
        return calculate_information_conductivity(
            self.history,
            method='temporal' if method == 'simple' else method
        )
    
    def get_state(self, timestep: Optional[int] = None) -> np.ndarray:
        """Get grid state at specified timestep
        
        Args:
            timestep: Timestep to retrieve (None for current state)
            
        Returns:
            np.ndarray: Grid state at specified timestep
            
        Raises:
            IndexError: If timestep is out of range
        """
        if timestep is None:
            return self.grid.copy()
        
        if 0 <= timestep < len(self.history):
            return self.history[timestep].copy()
        else:
            raise IndexError(f"Timestep {timestep} out of range [0, {len(self.history)})")
    
    def reset(self, random_seed: Optional[int] = None) -> None:
        """Reset the cellular automaton to initial random state
        
        Args:
            random_seed: New random seed (None to use different random state)
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        self.grid = np.random.random(self.grid_size)
        self.history = [self.grid.copy()]
    
    def get_statistics(self) -> dict:
        """Get comprehensive statistics about the current CA state
        
        Returns:
            dict: Statistical summary of the system
        """
        return {
            'grid_size': self.grid_size,
            'interaction_strength': self.interaction_strength,
            'timesteps': len(self.history) - 1,
            'current_mean': float(np.mean(self.grid)),
            'current_std': float(np.std(self.grid)),
            'current_min': float(np.min(self.grid)),
            'current_max': float(np.max(self.grid)),
            'info_conductivity_simple': self.information_conductivity('simple'),
            'info_conductivity_entropy': self.information_conductivity('entropy'),
            'info_conductivity_gradient': self.information_conductivity('gradient'),
        }


def example_usage():
    """Example usage of CA2D class"""
    print("=== DA-P_Satulon CA-2D Example ===")
    
    # Create CA instance
    ca = CA2D(grid_size=(30, 30), interaction_strength=0.3, random_seed=42)
    print(f"Initialized CA with grid size: {ca.grid_size}")
    print(f"Interaction strength: {ca.interaction_strength}")
    
    # Run simulation
    print("\nRunning 10 iterations...")
    ca.update(10)
    
    # Calculate information conductivity with different methods
    methods = ['simple', 'entropy', 'gradient']
    print(f"\nFinal information conductivity:")
    for method in methods:
        conductivity = ca.information_conductivity(method)
        print(f"  {method.capitalize()}: {conductivity:.4f}")
    
    # Get statistics
    stats = ca.get_statistics()
    print(f"\nSystem statistics:")
    print(f"  Timesteps: {stats['timesteps']}")
    print(f"  Current mean: {stats['current_mean']:.4f}")
    print(f"  Current std: {stats['current_std']:.4f}")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    example_usage()
