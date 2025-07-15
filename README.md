# Da-P_Satulon

**Satulon = "the particle that saturates space into one"**

Information Conductivity in 2D/3D Cellular Automata - G1-G5 Research Phases

[![Tests](https://github.com/Da-P-AIP/Da-P_Satulon/actions/workflows/test.yml/badge.svg)](https://github.com/Da-P-AIP/Da-P_Satulon/actions/workflows/test.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Paper](https://img.shields.io/badge/paper-LaTeX-green)](paper_G1/latex/main.tex)

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

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- NumPy, Matplotlib
- (Optional) Jupyter Notebook

### Installation
```bash
git clone https://github.com/Da-P-AIP/Da-P_Satulon.git
cd Da-P_Satulon
pip install -r requirements.txt
```

### Basic Usage
```bash
# Run single CA experiment
python code/ca_2d/grid.py

# Run parameter sweep experiments
python run_experiments.py --grid-size 50 --iterations 100

# View results
ls results/run001/
```

### Quick Import Test
```bash
# Test the installation
python -c "from code.ca_2d import CA2D, create_ca; ca = create_ca(30, 0.5); print(f'✅ Import successful! Grid: {ca.grid_size}')"
```

## 📁 Project Structure

```
Da-P_Satulon/
├── code/
│   ├── ca_2d/           # 2D Cellular Automata implementation
│   │   ├── __init__.py  # Module exports
│   │   ├── grid.py      # Core CA class
│   │   └── utils.py     # Utility functions
│   └── ca_3d/           # 3D extension (G3+)
├── results/             # Experimental outputs
│   ├── README.md        # Data format specification
│   ├── run001/          # Experiment run directory
│   │   ├── grid_*.npy   # Grid state snapshots
│   │   ├── cond.csv     # Information conductivity data
│   │   └── plots/       # Visualization outputs
│   └── ...
├── paper_G1/            # Paper drafts and LaTeX
│   ├── latex/
│   │   ├── main.tex     # Main paper (revtex4-2)
│   │   └── bib.bib      # Bibliography
│   └── figures/         # Paper figures
├── .github/             # GitHub workflows & templates
│   ├── ISSUE_TEMPLATE/  # YAML issue forms
│   └── workflows/       # CI/CD pipelines
├── tests/               # Unit tests
├── docs/                # Documentation
└── run_experiments.py   # Main experiment runner
```

## 🔬 Current Features (G1 Phase)

- [x] **YAML Issue Templates** - Structured task management
- [x] **CI/CD Pipeline** - Automated testing on Python 3.8-3.11 ([workflow](.github/workflows/test.yml))
- [x] **Module Structure** - Clean imports with `from code.ca_2d import CA2D`
- [x] **LaTeX Paper Framework** - Publication-ready template ([paper](paper_G1/latex/main.tex))
- [ ] **CA-2D Implementation** - Core cellular automata class ([#1](https://github.com/Da-P-AIP/Da-P_Satulon/issues/1))
- [ ] **Data Output Specification** - Standardized result formats ([#2](https://github.com/Da-P-AIP/Da-P_Satulon/issues/2))
- [ ] **Experiment Runner** - Automated parameter sweeps ([#3](https://github.com/Da-P-AIP/Da-P_Satulon/issues/3))
- [ ] **Enhanced CI/CD** - Quality assurance expansion ([#4](https://github.com/Da-P-AIP/Da-P_Satulon/issues/4))
- [ ] **Overleaf Integration** - Collaborative writing setup ([#5](https://github.com/Da-P-AIP/Da-P_Satulon/issues/5))

## 📊 Information Conductivity

**Core Concept**: 情報伝導度は、CA内での情報伝達効率を定量化する新しい指標です。

```python
# Quick example
from code.ca_2d import create_ca, information_conductivity_stub

ca = create_ca(grid_size=30, interaction_strength=0.5)
ca.update(10)
conductivity = information_conductivity_stub(ca.grid)
print(f"Information conductivity: {conductivity:.4f}")
```

詳細な定義とアルゴリズムはG1フェーズで策定されます。

## 🧪 Running Experiments

### Simple Parameter Sweep
```bash
# Quick test (small grid)
python run_experiments.py --grid-size 10 --iterations 5 --interaction-steps 3

# Full experiment
python run_experiments.py \
  --grid-size 50 \
  --iterations 100 \
  --interaction-min 0.1 \
  --interaction-max 1.0 \
  --interaction-steps 10 \
  --save-frames \
  --create-gif
```

### Viewing Results
```bash
# Check experiment output
ls results/run*/
cat results/run001/results_summary.csv

# View plots
open results/run001/plots/summary.png  # macOS
xdg-open results/run001/plots/summary.png  # Linux
```

## 🤝 Contributing

1. 新しいタスクは[Issue Template](https://github.com/Da-P-AIP/Da-P_Satulon/issues/new/choose)を使用
2. ブランチ命名: `g1/feature-name`, `g2/analysis-type`
3. PR時に `Closes #<issue-number>` を記載
4. コードレビュー後にマージ

### Development Workflow
```bash
# Create feature branch
git checkout -b g1/my-feature

# Make changes and test
python code/ca_2d/grid.py
python run_experiments.py --grid-size 5 --iterations 3

# Commit and push
git add .
git commit -m "Implement feature X for Issue #N"
git push origin g1/my-feature
```

## 📚 Documentation & Paper

- **Paper Draft**: [LaTeX Source](paper_G1/latex/main.tex) (RevTeX4-2 format)
- **Overleaf Project**: [TBD - Will be added in Issue #5]
- **Zotero Group**: [TBD - Will be set up in Issue #5]
- **API Documentation**: [Code README](code/README.md)

## 📈 Development Status

![GitHub Issues](https://img.shields.io/github/issues/Da-P-AIP/Da-P_Satulon)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Da-P-AIP/Da-P_Satulon)
![Last Commit](https://img.shields.io/github/last-commit/Da-P-AIP/Da-P_Satulon)

**Current Milestone**: G1-Draft (Target: Oct 5, 2025)

## 🔧 System Requirements

- **Python**: 3.8+ (tested on 3.8, 3.9, 3.10, 3.11)
- **Memory**: ~100MB for basic experiments, ~1GB for large parameter sweeps
- **Storage**: ~10MB per experiment run (with frame saving)
- **OS**: Cross-platform (Linux, macOS, Windows)

## 📄 License

[MIT License](LICENSE) - Feel free to use for research and educational purposes.

## 📧 Contact

For questions or collaborations, please open an issue or contact the project maintainers.

**Research Team**: Da-P-AIP Organization  
**Project Repository**: https://github.com/Da-P-AIP/Da-P_Satulon