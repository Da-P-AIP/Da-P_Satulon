# Da-P_Satulon

**Satulon = "the particle that saturates space into one"**

Information Conductivity in 2D/3D Cellular Automata - G1-G5 Research Phases

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

## 📁 Project Structure

```
Da-P_Satulon/
├── code/
│   ├── ca_2d/           # 2D Cellular Automata implementation
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
├── tests/               # Unit tests
├── docs/                # Documentation
├── .github/             # GitHub workflows & templates
└── run_experiments.py   # Main experiment runner
```

## 🔬 Current Features (G1 Phase)

- [x] **YAML Issue Templates** - Structured task management
- [ ] **CA-2D Implementation** - Core cellular automata class ([#1](https://github.com/Da-P-AIP/Da-P_Satulon/issues/1))
- [ ] **Data Output Specification** - Standardized result formats ([#2](https://github.com/Da-P-AIP/Da-P_Satulon/issues/2))
- [ ] **Experiment Runner** - Automated parameter sweeps ([#3](https://github.com/Da-P-AIP/Da-P_Satulon/issues/3))
- [ ] **CI/CD Pipeline** - Quality assurance ([#4](https://github.com/Da-P-AIP/Da-P_Satulon/issues/4))
- [ ] **LaTeX Framework** - Paper writing infrastructure ([#5](https://github.com/Da-P-AIP/Da-P_Satulon/issues/5))

## 📊 Information Conductivity

**Core Concept**: 情報伝導度は、CA内での情報伝達効率を定量化する新しい指標です。

```python
# Stub implementation (G1)
def information_conductivity(grid_state):
    """Calculate information conductivity of CA grid"""
    return grid_state.mean()  # Placeholder
```

詳細な定義とアルゴリズムはG1フェーズで策定されます。

## 🤝 Contributing

1. 新しいタスクは[Issue Template](https://github.com/Da-P-AIP/Da-P_Satulon/issues/new/choose)を使用
2. ブランチ命名: `g1/feature-name`, `g2/analysis-type`
3. PR時に `Closes #<issue-number>` を記載
4. コードレビュー後にマージ

## 📚 Documentation & Paper

- **Overleaf Project**: [TBD - Will be added in Issue #5]
- **Zotero Group**: [TBD - Will be set up in Issue #5]
- **API Documentation**: Coming with G1 implementation

## 📈 Development Status

![GitHub Issues](https://img.shields.io/github/issues/Da-P-AIP/Da-P_Satulon)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Da-P-AIP/Da-P_Satulon)

**Current Milestone**: G1-Draft (Target: Oct 5, 2025)

---

## 📄 License

[MIT License] - Feel free to use for research and educational purposes.

## 📧 Contact

For questions or collaborations, please open an issue or contact the project maintainers.

**Research Team**: Da-P-AIP Organization