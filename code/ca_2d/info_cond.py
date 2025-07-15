"""
Information Conductivity Calculation Module

This module provides various implementations of information conductivity
metrics for cellular automata analysis.

Author: Da-P-AIP Research Team
Version: 0.2.0 (G1 Phase Enhancement)
"""

import numpy as np
from typing import Union, Tuple, Optional
import warnings


def simple_conductivity(grid_state: np.ndarray) -> float:
    """
    Simple information conductivity based on mean activity
    
    This is the G1 phase implementation used as baseline.
    
    Args:
        grid_state: 2D numpy array representing CA grid
        
    Returns:
        float: Mean activity across the grid
    """
    return float(np.mean(grid_state))


def entropy_conductivity(grid_state: np.ndarray, 
                        bins: int = 10,
                        method: str = 'histogram') -> float:
    """
    Entropy-based information conductivity
    
    Calculates Shannon entropy of the grid state distribution.
    
    Args:
        grid_state: 2D numpy array representing CA grid
        bins: Number of bins for histogram (for continuous values)
        method: Method for entropy calculation ('histogram', 'gaussian')
        
    Returns:
        float: Entropy-based conductivity measure
    """
    if method == 'histogram':
        # Flatten grid and create histogram
        flat_state = grid_state.flatten()
        counts, _ = np.histogram(flat_state, bins=bins, density=True)
        
        # Remove zero counts to avoid log(0)
        counts = counts[counts > 0]
        
        # Calculate Shannon entropy
        entropy = -np.sum(counts * np.log2(counts + 1e-12))
        
        # Normalize by maximum possible entropy
        max_entropy = np.log2(bins)
        return entropy / max_entropy if max_entropy > 0 else 0.0
        
    elif method == 'gaussian':
        # Assume Gaussian distribution and calculate differential entropy
        var = np.var(grid_state)
        if var <= 0:
            return 0.0
        # Differential entropy of Gaussian: 0.5 * log(2πeσ²)
        entropy = 0.5 * np.log2(2 * np.pi * np.e * var)
        return max(0.0, entropy)  # Ensure non-negative
    
    else:
        raise ValueError(f"Unknown entropy method: {method}")


def spatial_gradient_conductivity(grid_state: np.ndarray,
                                 interaction_strength: float = 1.0) -> float:
    """
    Spatial gradient-based information conductivity
    
    Measures information flow based on spatial gradients in the grid.
    
    Args:
        grid_state: 2D numpy array representing CA grid
        interaction_strength: Weight for spatial coupling
        
    Returns:
        float: Gradient-based conductivity measure
    """
    # Calculate gradients in x and y directions
    grad_x, grad_y = np.gradient(grid_state)
    
    # Calculate magnitude of gradient field
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    # Information conductivity as mean gradient weighted by interaction
    conductivity = interaction_strength * np.mean(grad_magnitude)
    
    return float(conductivity)


def temporal_conductivity(grid_history: list,
                         window_size: int = 5,
                         method: str = 'variance') -> np.ndarray:
    """
    Temporal information conductivity analysis
    
    Analyzes how information conductivity changes over time.
    
    Args:
        grid_history: List of grid states over time
        window_size: Size of sliding window for temporal analysis
        method: Method for temporal analysis ('variance', 'entropy', 'simple')
        
    Returns:
        np.ndarray: Time series of conductivity values
    """
    if len(grid_history) < 2:
        warnings.warn("Need at least 2 time steps for temporal analysis")
        return np.array([simple_conductivity(grid_history[0])])
    
    conductivities = []
    
    for i, grid in enumerate(grid_history):
        if method == 'simple':
            cond = simple_conductivity(grid)
        elif method == 'entropy':
            cond = entropy_conductivity(grid)
        elif method == 'variance':
            # Use local variance as proxy for information content
            cond = float(np.var(grid))
        else:
            raise ValueError(f"Unknown temporal method: {method}")
            
        conductivities.append(cond)
    
    return np.array(conductivities)


def transfer_entropy_approx(source_region: np.ndarray,
                           target_region: np.ndarray,
                           lag: int = 1) -> float:
    """
    Approximate transfer entropy between regions
    
    Simplified transfer entropy calculation for G1 phase.
    
    Args:
        source_region: Source region states over time
        target_region: Target region states over time  
        lag: Time lag for transfer entropy calculation
        
    Returns:
        float: Approximate transfer entropy
    """
    if len(source_region) <= lag or len(target_region) <= lag:
        return 0.0
    
    # Simple correlation-based approximation
    # In G2, this will be replaced with proper transfer entropy
    source_diff = np.diff(source_region, axis=0)
    target_diff = np.diff(target_region, axis=0)
    
    if len(source_diff) == 0 or len(target_diff) == 0:
        return 0.0
    
    # Cross-correlation as proxy for transfer entropy
    correlation = np.corrcoef(source_diff[:-lag].flatten(), 
                             target_diff[lag:].flatten())[0, 1]
    
    # Convert correlation to information-like measure
    if np.isnan(correlation):
        return 0.0
    
    # Information-theoretic interpretation: -log(1-|r|²)
    r_squared = correlation**2
    transfer_info = -np.log(1 - r_squared + 1e-12)
    
    return float(max(0.0, transfer_info))


def multi_scale_conductivity(grid_state: np.ndarray,
                           scales: Optional[list] = None) -> dict:
    """
    Multi-scale information conductivity analysis
    
    Analyzes conductivity at different spatial scales.
    
    Args:
        grid_state: 2D numpy array representing CA grid
        scales: List of scale factors (default: [1, 2, 4])
        
    Returns:
        dict: Conductivity values at different scales
    """
    if scales is None:
        scales = [1, 2, 4]
    
    results = {}
    
    for scale in scales:
        if scale == 1:
            # Original resolution
            scaled_grid = grid_state
        else:
            # Downsample by averaging over scale×scale blocks
            h, w = grid_state.shape
            new_h, new_w = h // scale, w // scale
            
            if new_h == 0 or new_w == 0:
                continue
                
            scaled_grid = np.zeros((new_h, new_w))
            for i in range(new_h):
                for j in range(new_w):
                    block = grid_state[i*scale:(i+1)*scale, 
                                     j*scale:(j+1)*scale]
                    scaled_grid[i, j] = np.mean(block)
        
        # Calculate conductivity at this scale
        cond_simple = simple_conductivity(scaled_grid)
        cond_entropy = entropy_conductivity(scaled_grid)
        cond_gradient = spatial_gradient_conductivity(scaled_grid)
        
        results[f'scale_{scale}'] = {
            'simple': cond_simple,
            'entropy': cond_entropy,
            'gradient': cond_gradient,
            'grid_size': scaled_grid.shape
        }
    
    return results


# Main interface function for compatibility
def calculate_information_conductivity(grid_state: Union[np.ndarray, list],
                                     method: str = 'simple',
                                     **kwargs) -> Union[float, np.ndarray]:
    """
    Main interface for information conductivity calculation
    
    Args:
        grid_state: Grid state(s) - single array or list of arrays
        method: Calculation method ('simple', 'entropy', 'gradient', 'temporal')
        **kwargs: Additional parameters for specific methods
        
    Returns:
        float or np.ndarray: Conductivity value(s)
    """
    if method == 'simple':
        if isinstance(grid_state, list):
            return np.array([simple_conductivity(grid) for grid in grid_state])
        return simple_conductivity(grid_state)
    
    elif method == 'entropy':
        if isinstance(grid_state, list):
            return np.array([entropy_conductivity(grid, **kwargs) 
                           for grid in grid_state])
        return entropy_conductivity(grid_state, **kwargs)
    
    elif method == 'gradient':
        if isinstance(grid_state, list):
            return np.array([spatial_gradient_conductivity(grid, **kwargs)
                           for grid in grid_state])
        return spatial_gradient_conductivity(grid_state, **kwargs)
    
    elif method == 'temporal':
        if not isinstance(grid_state, list):
            raise ValueError("Temporal method requires list of grid states")
        return temporal_conductivity(grid_state, **kwargs)
    
    elif method == 'multiscale':
        if isinstance(grid_state, list):
            raise ValueError("Multiscale method works on single grid state")
        return multi_scale_conductivity(grid_state, **kwargs)
    
    else:
        raise ValueError(f"Unknown method: {method}")


# Backward compatibility
information_conductivity_stub = simple_conductivity


if __name__ == "__main__":
    # Demo usage
    print("=== Information Conductivity Demo ===")
    
    # Create test grid
    np.random.seed(42)
    test_grid = np.random.random((10, 10))
    
    # Test different methods
    methods = ['simple', 'entropy', 'gradient']
    for method in methods:
        result = calculate_information_conductivity(test_grid, method=method)
        print(f"{method.capitalize()} conductivity: {result:.4f}")
    
    # Test temporal analysis
    grid_history = [np.random.random((5, 5)) for _ in range(10)]
    temporal_result = calculate_information_conductivity(
        grid_history, method='temporal'
    )
    print(f"Temporal conductivity series length: {len(temporal_result)}")
    
    # Test multiscale analysis
    multiscale_result = calculate_information_conductivity(
        test_grid, method='multiscale'
    )
    print(f"Multiscale analysis scales: {list(multiscale_result.keys())}")
    
    print("=== Demo Complete ===")
