"""
Da-P_Satulon 3D Cellular Automata Package
G2 Phase Implementation

This package provides comprehensive 3D cellular automata capabilities:
- GPU-accelerated computation (Issue #12)
- Advanced visualization (Issue #13)
- Enhanced statistical analysis (Issue #14)
"""

__version__ = "2.0.0"
__author__ = "Da-P-AIP Research Team"
__email__ = "research@da-p-aip.org"

# Import main classes
try:
    from .gpu_acceleration import GPUAcceleratedCA3D
except ImportError:
    print("⚠️  GPU acceleration module not available")
    GPUAcceleratedCA3D = None

try:
    from .visualization import CA3DVisualizer
except ImportError:
    print("⚠️  Visualization module not available")
    CA3DVisualizer = None

try:
    from .statistical_analysis import AdvancedStatisticalAnalyzer
except ImportError:
    print("⚠️  Statistical analysis module not available")
    AdvancedStatisticalAnalyzer = None

# Package metadata
__all__ = [
    'GPUAcceleratedCA3D',
    'CA3DVisualizer', 
    'AdvancedStatisticalAnalyzer'
]

# Version info
version_info = (2, 0, 0)

print(f"📦 Da-P_Satulon CA-3D v{__version__} loaded")
print(f"🚀 G2 Phase: GPU + Visualization + Analysis")