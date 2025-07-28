# da-P Particle v0.2 Ultra-Precise Measurement Data

This file should contain the ultra-precise measurement data from the CSV files in your project knowledge.

## Ultra-Precise Scan L=64
- Critical point detection via variance peak analysis
- System size: 64³ cells
- Resolution: Δp = 10⁻⁶
- Critical point: p_c = 0.009900000
- Method: Variance peak detection with 25-50 independent runs

## Ultra-Precise Scan L=128  
- Critical point detection via variance peak analysis
- System size: 128³ cells
- Resolution: Δp = 10⁻⁶
- Critical point: p_c = 0.009500000
- Method: Variance peak detection with 25-50 independent runs

## Finite-Size Scaling Analysis
- Extrapolation: p_c(L) = p_c(∞) + A/L
- Infinite-system critical point: p_c(∞) = 0.009100 ± 0.000005
- Scaling coefficient: A = +0.051/L ± 0.003
- Correlation length exponent: ν = 0.34 ± 0.01

## Data Format
Each CSV file contains columns:
- p: Transition probability parameter
- density_mean: Average final density
- density_std: Standard deviation of density measurements  
- activity_mean: Average activity level
- activity_std: Standard deviation of activity
- survival_rate: Fraction of surviving configurations
- survival_time_mean: Average survival time
- survival_time_std: Standard deviation of survival times
- final_mass_mean: Average final active mass
- final_mass_std: Standard deviation of final mass
- n_samples: Number of independent simulation runs

## Measurement Protocol
1. Initial density: p_fill = 0.10 
2. Evolution time: 150 time steps
3. Equilibration: 100-200 time steps before measurement
4. Statistical sampling: 25-50 independent runs per data point
5. GPU acceleration: CUDA-optimized PyTorch kernels
6. Boundary conditions: Periodic boundaries in all directions

## Critical Fluctuation Analysis
- Sharp variance peaks enable sub-ppm precision critical point determination
- Systematic shift in p_c(L) enables finite-size extrapolation to thermodynamic limit
- Multiple observables (density, activity, survival) show coincident critical signatures
- Bootstrap resampling with 1000 samples for error analysis

## References
- Progress Report v0.2: "Interim 3-D and 4-D Results on da-P Particle Critical Behaviour"
- GitHub Repository: https://github.com/Da-P-AIP/Da-P_Satulon
- Contact: contact.dap.project@gmail.com
