"""
2D Cellular Automata with Information Conductivity

This module implements the core CA-2D class for studying information 
conductivity in 2D cellular automata systems.

Author: Da-P-AIP Research Team
Version: 0.1.0 (G1 Phase)
"""

import numpy as np
from typing import Tuple, Optional


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
        self.interaction_strength = interaction_strength
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
        
        TODO (G1): Implement actual CA update rules with interaction_strength
        Currently: Placeholder implementation
        """
        # STUB: Simple diffusion-like update
        # This will be replaced with proper CA rules in Issue #1
        h, w = self.grid_size
        new_grid = self.grid.copy()
        
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                # Simple neighbor averaging with interaction strength
                neighbors = (self.grid[i-1, j] + self.grid[i+1, j] + 
                           self.grid[i, j-1] + self.grid[i, j+1])
                new_grid[i, j] = (self.grid[i, j] * (1 - self.interaction_strength) + 
                                neighbors * self.interaction_strength / 4)
        
        self.grid = new_grid
    
    def information_conductivity(self) -> float:
        """Calculate information conductivity of current grid state
        
        Returns:
            float: Information conductivity measure
            
        TODO (G1): Implement proper information conductivity metric
        Currently: Placeholder returning mean activity
        """
        # STUB: Simple mean-based placeholder
        # This will be replaced with proper information theory metrics
        return float(self.grid.mean())
    
    def get_conductivity_series(self) -> np.ndarray:
        """Calculate information conductivity for all states in history
        
        Returns:
            np.ndarray: Time series of conductivity values
        """
        conductivities = []
        current_grid = self.grid
        
        for state in self.history:
            self.grid = state
            conductivities.append(self.information_conductivity())
        
        self.grid = current_grid  # Restore current state
        return np.array(conductivities)
    
    def get_state(self, timestep: Optional[int] = None) -> np.ndarray:
        """Get grid state at specified timestep
        
        Args:
            timestep: Timestep to retrieve (None for current state)
            
        Returns:
            np.ndarray: Grid state at specified timestep
        """
        if timestep is None:
            return self.grid.copy()
        return self.history[timestep].copy()
    
    def reset(self, random_seed: Optional[int] = None) -> None:
        """Reset the cellular automaton to initial random state
        
        Args:
            random_seed: New random seed (None to use different random state)
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        self.grid = np.random.random(self.grid_size)
        self.history = [self.grid.copy()]


def example_usage():
    """Example usage of CA2D class"""
    print("=== DA-P_Satulon CA-2D Example ===")
    
    # Create CA instance
    ca = CA2D(grid_size=(30, 30), interaction_strength=0.3, random_seed=42)
    print(f"Initialized CA with grid size: {ca.grid_size}")
    print(f"Interaction strength: {ca.interaction_strength}")
    
    # Run simulation
    print("\\nRunning 10 iterations...")
    ca.update(10)
    
    # Calculate information conductivity
    final_conductivity = ca.information_conductivity()
    conductivity_series = ca.get_conductivity_series()
    
    print(f"Final information conductivity: {final_conductivity:.4f}")
    print(f"Conductivity trend: {conductivity_series[0]:.4f} -> {conductivity_series[-1]:.4f}")
    print(f"Total states in history: {len(ca.history)}")
    
    print("\\n=== Example Complete ===")


if __name__ == "__main__":
    example_usage()
