# Da-P_Satulon

**Satulon = "the particle that saturates space into one"**

Information Conductivity in 2D/3D Cellular Automata - G1-G5 Research Phases

[![Tests](https://github.com/Da-P-AIP/Da-P_Satulon/actions/workflows/test.yml/badge.svg)](https://github.com/Da-P-AIP/Da-P_Satulon/actions/workflows/test.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Paper](https://img.shields.io/badge/paper-LaTeX-green)](paper_G1/latex/main.tex)
[![Notebook Demo](https://img.shields.io/badge/demo-Jupyter-orange)](examples/notebook/sweep_demo.ipynb)

## 🎯 Project Overview

この研究プロジェクトは、2次元および3次元セルラーオートマタ（CA）における「情報伝導度」の概念を探求します。相互作用強度と情報伝達効率の関係を定量化し、新しい物理現象の理解を目指します。

## 📋 Research Phases (Roadmap)

| Phase | Focus | Timeline | Status |
|-------|-------|----------|---------|
| **G1** | CA-2D Minimal Implementation | Aug 2025 | 🔄 Active |
| **G2** | Parameter Analysis & Optimization | Sep 2025 | ⏳ Planned |
| **G3** | 3D Extension & Advanced Metrics | Oct 2025 | ⏳ Planned |
| **G4** | Theoretical Framework | Nov 2025 | ⏳ Planned |
| **G5** | Paper Completion & Publication | Dec 2025 | ⏳ Planned |

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- Git

### Installation
```bash
git clone https://github.com/Da-P-AIP/Da-P_Satulon.git
cd Da-P_Satulon
pip install -r requirements.txt
```

### Verify Installation & CA-2D Core
```bash
# Test core CA-2D functionality (Issue #1)
python -c "from code.ca_2d import CA2D, create_ca; print('✅ CA-2D core ready!')"

# Run CA-2D demo with interaction_strength
python -c "from code.ca_2d import demo_ca_functionality; demo_ca_functionality()"

# Test information_conductivity_stub
python -c "from code.ca_2d import information_conductivity_stub; import numpy as np; print(f'Stub test: {information_conductivity_stub(np.random.random((5,5))):.4f}')"
```

### CA-2D Usage Examples
```python
# Basic CA-2D usage (Issue #1 implementation)
from code.ca_2d import create_ca, CA2D

# Create CA with specific parameters
ca = create_ca(grid_size=30, interaction_strength=0.4, seed=42)

# Run simulation with interaction_strength affecting updates
ca.update(20)

# Calculate information conductivity (stub implementation)
conductivity = ca.information_conductivity()
print(f"Information conductivity: {conductivity:.4f}")

# Get time series analysis
series = ca.get_conductivity_series()
print(f"Conductivity evolution: {series[0]:.3f} → {series[-1]:.3f}")

# System statistics
stats = ca.get_statistics()
print(f"Grid: {stats['grid_size']}, Timesteps: {stats['timesteps']}")
```

### Quick Experiment
```bash
# Run quick experiment (30 seconds) 
python run_experiments.py --grid-size 20 --iterations 20 --interaction-steps 3 --verbose
```

### View Results
```bash
# Check results
ls results/run001/
cat results/run001/results_summary.csv

# Open plots
open results/run001/plots/summary.png     # macOS
```

**🎉 Congratulations!** You've just run your first information conductivity experiment.

## 📊 Advanced Usage

### Research-Grade Experiments
```bash
# Comprehensive parameter sweep
python run_experiments.py \
  --grid-size 50 \
  --iterations 100 \
  --interaction-min 0.1 \
  --interaction-max 1.0 \
  --interaction-steps 10 \
  --conductivity-method entropy \
  --multiscale-analysis \
  --save-frames \
  --create-gif \
  --verbose
```

### Python API
```python
from code.ca_2d import create_ca
from code.ca_2d.info_cond import calculate_information_conductivity

# Create and run CA
ca = create_ca(grid_size=50, interaction_strength=0.5, seed=42)
ca.update(100)

# Analyze with multiple methods
for method in ['simple', 'entropy', 'gradient']:
    conductivity = calculate_information_conductivity(ca.grid, method=method)
    print(f"{method}: {conductivity:.4f}")
```

### Interactive Analysis
Open the [Jupyter Demo Notebook](examples/notebook/sweep_demo.ipynb) for interactive parameter sweeps and publication-quality visualizations.

## 📁 Project Structure

```
Da-P_Satulon/
├── 🔬 Research Code
│   ├── code/ca_2d/          # 2D Cellular Automata (✅ Issue #1 Complete)
│   │   ├── __init__.py      # Clean imports: `from code.ca_2d import CA2D`
│   │   ├── grid.py          # Core CA implementation with interaction_strength
│   │   └── info_cond.py     # Information conductivity metrics & stub
│   └── code/ca_3d/          # 3D extension (G3+)
├── 📊 Results & Analysis
│   ├── results/README.md    # Data format specification
│   ├── examples/notebook/   # Interactive Jupyter demos
│   │   └── sweep_demo.ipynb # Parameter sweep demonstration
│   └── docs/
│       ├── usage.md         # 5-minute quick start guide
│       └── metrics.md       # Mathematical framework
├── 📄 Publication
│   ├── paper_G1/latex/     # LaTeX manuscript
│   │   ├── main.tex         # Main paper (RevTeX4-2)
│   │   └── bib.bib          # Bibliography
│   └── paper_G1/figures/    # Paper figures
├── 🛠️ Development
│   ├── .github/workflows/   # CI/CD pipelines
│   ├── tests/               # Unit tests (pytest)
│   ├── .flake8             # Code quality config
│   └── requirements.txt     # Pinned dependencies
└── run_experiments.py       # Main experiment runner
```

## 🔬 Current Features (G1 Phase)

- [x] **Enhanced YAML Issue Templates** - Structured task management
- [x] **CI/CD Pipeline** - Automated testing on Python 3.8-3.11 ([workflow](.github/workflows/test.yml))
- [x] **Information Conductivity Framework** - Multiple calculation methods ([docs](docs/metrics.md))
- [x] **Advanced Experiment Runner** - Parameter sweeps with visualization ([enhanced](run_experiments.py))
- [x] **Interactive Jupyter Demo** - Publication-ready analysis ([notebook](examples/notebook/sweep_demo.ipynb))
- [x] **Comprehensive Documentation** - 5-minute quick start ([guide](docs/usage.md))
- [x] **LaTeX Paper Framework** - Publication-ready template ([paper](paper_G1/latex/main.tex))
- [x] **CA-2D Core Implementation** - Cellular automata engine with interaction_strength ([#1](https://github.com/Da-P-AIP/Da-P_Satulon/issues/1)) ✅
- [ ] **Data Output Specification** - Standardized result formats ([#2](https://github.com/Da-P-AIP/Da-P_Satulon/issues/2))
- [ ] **Enhanced run_experiments.py** - CLI with full parameter support ([#3](https://github.com/Da-P-AIP/Da-P_Satulon/issues/3))
- [ ] **CI Workflow Implementation** - Automated testing pipeline ([#4](https://github.com/Da-P-AIP/Da-P_Satulon/issues/4))
- [ ] **Overleaf Integration** - Collaborative writing setup ([#5](https://github.com/Da-P-AIP/Da-P_Satulon/issues/5))

## 📊 Information Conductivity Methods

The framework provides multiple approaches to quantify information transfer:

| Method | Description | Use Case |
|--------|-------------|----------|
| **Simple** | Mean activity across grid | Baseline comparison |
| **Entropy** | Shannon entropy of state distribution | Information content analysis |
| **Gradient** | Spatial gradient magnitude | Flow pattern detection |
| **Temporal** | Time series analysis | Evolution dynamics |
| **Multiscale** | Cross-scale information flow | Hierarchical analysis |

### Quick Method Comparison
```bash
# Compare all methods on same data
python run_experiments.py --grid-size 30 --iterations 50 --interaction-steps 5 --conductivity-method entropy
python run_experiments.py --grid-size 30 --iterations 50 --interaction-steps 5 --conductivity-method gradient --run-id method_gradient
python run_experiments.py --grid-size 30 --iterations 50 --interaction-steps 5 --conductivity-method simple --run-id method_simple
```

## 🧪 Research Applications

### Phase Transition Studies
```bash
# Fine-grained analysis around critical points
python run_experiments.py \
  --interaction-min 0.25 \
  --interaction-max 0.35 \
  --interaction-steps 20 \
  --iterations 200 \
  --conductivity-method entropy
```

### Scalability Analysis
```bash
# Test different grid sizes
for size in 20 50 100 200; do
  python run_experiments.py \
    --grid-size $size \
    --iterations 100 \
    --interaction-steps 10 \
    --run-id "scale_${size}"
done
```

### Method Validation
```bash
# Cross-validate different approaches
for method in simple entropy gradient; do
  python run_experiments.py \
    --conductivity-method $method \
    --random-seed 42 \
    --run-id "validation_${method}"
done
```

## 🎓 Learning Path

### Beginner (First Hour)
1. **Complete 5-minute quick start** above
2. **Test CA-2D core**: Run `python -c "from code.ca_2d import demo_ca_functionality; demo_ca_functionality()"`
3. **Run basic parameter sweep**: `python run_experiments.py --grid-size 30 --iterations 50`
4. **Explore results**: Check `results/run001/` files
5. **Read documentation**: [Usage Guide](docs/usage.md)

### Intermediate (First Week)
1. **Try different methods**: Run experiments with `--conductivity-method entropy`
2. **Use Python API**: Import and run CA simulations interactively
3. **Open Jupyter demo**: Work through [sweep_demo.ipynb](examples/notebook/sweep_demo.ipynb)
4. **Understand theory**: Read [Mathematical Framework](docs/metrics.md)

### Advanced (Research Level)
1. **Design custom experiments**: Modify `run_experiments.py` for specific research questions
2. **Implement new metrics**: Extend `info_cond.py` with novel conductivity measures
3. **Contribute to paper**: Edit [LaTeX manuscript](paper_G1/latex/main.tex)
4. **Scale up studies**: Run large-parameter sweeps with HPC resources

## 🤝 Contributing

We welcome contributions from researchers, students, and practitioners!

### Development Workflow
```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/Da-P_Satulon.git
cd Da-P_Satulon

# 2. Create feature branch
git checkout -b g1/my-awesome-feature

# 3. Make changes and test
python -m pytest tests/
python run_experiments.py --grid-size 10 --iterations 5

# 4. Submit pull request
git push origin g1/my-awesome-feature
# Open PR on GitHub with "Closes #issue-number"
```

### Contribution Areas
- **🔬 Algorithm Development**: New CA rules, conductivity metrics
- **📊 Analysis Tools**: Visualization, statistical methods
- **📚 Documentation**: Tutorials, examples, guides
- **🧪 Validation**: Theoretical analysis, benchmarking
- **📄 Paper Writing**: Research manuscript, figures

### Creating Issues
Use our [YAML Issue Templates](https://github.com/Da-P-AIP/Da-P_Satulon/issues/new/choose) for:
- **Satulon Task**: Research tasks with structured breakdown
- **Bug reports**: Technical issues
- **Feature requests**: New functionality

## 📚 Documentation & Resources

- **📖 Complete Usage Guide**: [docs/usage.md](docs/usage.md)
- **🔬 Mathematical Framework**: [docs/metrics.md](docs/metrics.md)
- **💻 Code Documentation**: [code/README.md](code/README.md)
- **📊 Data Specification**: [results/README.md](results/README.md)
- **📄 Paper Draft**: [paper_G1/latex/main.tex](paper_G1/latex/main.tex)
- **🎓 Interactive Demo**: [examples/notebook/sweep_demo.ipynb](examples/notebook/sweep_demo.ipynb)

## 📈 Development Status

![GitHub Issues](https://img.shields.io/github/issues/Da-P-AIP/Da-P_Satulon)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Da-P-AIP/Da-P_Satulon)
![Last Commit](https://img.shields.io/github/last-commit/Da-P-AIP/Da-P_Satulon)

**Current Milestone**: G1-Draft (Target: Oct 5, 2025)

### Recent Updates
- ✅ CA-2D core implementation with interaction_strength (Issue #1)
- ✅ Enhanced experiment runner with multiple conductivity methods
- ✅ Comprehensive information conductivity framework
- ✅ Interactive Jupyter notebook for parameter sweeps
- ✅ Publication-ready LaTeX template with citations
- ✅ Complete usage documentation with 5-minute quickstart
- ✅ CI/CD pipeline with multi-Python testing

### Immediate Next Steps
1. **Set up data output specification** (Issue #2)
2. **Enhance run_experiments.py CLI** (Issue #3)
3. **Implement CI workflow** (Issue #4)
4. **Set up Overleaf integration** (Issue #5)

## 🔧 System Requirements

- **Python**: 3.8+ (tested on 3.8, 3.9, 3.10, 3.11)
- **Memory**: ~100MB for basic experiments, ~1GB for large parameter sweeps
- **Storage**: ~10MB per experiment run (with frame saving)
- **OS**: Cross-platform (Linux, macOS, Windows)

### Performance Notes
- Grid sizes up to 200×200 run efficiently on standard laptops
- Large parameter sweeps (50+ experiments) benefit from multicore systems
- GPU acceleration planned for G2+ phases

## 📄 License & Citation

This project is licensed under the [MIT License](LICENSE), making it freely available for research and educational use.

**If you use this code in academic research, please cite:**

```bibtex
@software{da_p_satulon_2025,
  title={Da-P\_Satulon: Information Conductivity in Cellular Automata},
  author={Da-P-AIP Research Team},
  year={2025},
  url={https://github.com/Da-P-AIP/Da-P_Satulon},
  note={Research software for studying information conductivity in 2D/3D cellular automata}
}
```

## 📧 Contact & Support

- **🐛 Issues**: [GitHub Issues](https://github.com/Da-P-AIP/Da-P_Satulon/issues) with detailed templates
- **💬 Discussions**: [GitHub Discussions](https://github.com/Da-P-AIP/Da-P_Satulon/discussions) for research questions
- **📧 Direct Contact**: Open an issue for collaboration inquiries

**Research Team**: Da-P-AIP Organization  
**Project Website**: https://github.com/Da-P-AIP/Da-P_Satulon

---

**🌟 Star this repository** if you find it useful for your research!  
**🔀 Fork and contribute** to advance the understanding of information conductivity in complex systems.
