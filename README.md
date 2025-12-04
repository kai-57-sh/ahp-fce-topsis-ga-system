# AHP-FCE-TOPSIS-GA Evaluation System

A comprehensive hybrid multi-criteria decision analysis system for evaluating unmanned combat system configurations using Analytic Hierarchy Process (AHP), Fuzzy Comprehensive Evaluation (FCE), Technique for Order Preference by Similarity to Ideal Solution (TOPSIS), and Genetic Algorithm (GA) optimization.

## 🚀 Features

- **AHP**: Calculate indicator weights from expert pairwise comparisons with consistency validation (CR < 0.1)
- **FCE**: Convert qualitative assessments (差/中/良/优) to quantitative scores using fuzzy membership functions
- **TOPSIS**: Rank configurations based on relative closeness to ideal solutions with vector normalization
- **GA**: Optimize system configurations under operational constraints using PyGAD
- **Comprehensive Validation**: Sensitivity analysis, jackknife validation, and audit trail logging
- **Report Generation**: Automated markdown and PDF report generation with methodology documentation

## 📋 System Requirements

- Python 3.8+
- NumPy ≥1.21
- Pandas ≥1.3
- PyGAD ≥2.10
- Matplotlib ≥3.5
- PyYAML ≥6.0

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ahp_fce_topsis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Validate installation:
```bash
python main.py --version
```

## 🎯 Quick Start

### 1. Evaluate Single Configuration
```bash
python main.py evaluate --schemes data/schemes/balanced_force.yaml
```

### 2. Compare Multiple Configurations
```bash
python main.py evaluate --schemes data/schemes/balanced_force.yaml data/schemes/high_endurance_force.yaml data/schemes/tech_lite_force.yaml
```

### 3. Optimize Configuration
```bash
python main.py optimize --scenario data/scenarios/strait_control.yaml --population 20 --generations 50
```

### 4. Generate Comprehensive Report
```bash
python main.py report --schemes data/schemes/balanced_force.yaml --output reports/comprehensive_report.md
```

### 5. Run Sensitivity Analysis
```bash
python main.py sensitivity --schemes data/schemes/balanced_force.yaml --perturbation 0.2
```

### 6. Visualize Results
```bash
python main.py visualize --schemes data/schemes/balanced_force.yaml data/schemes/high_endurance_force.yaml --output plots/comparison.png
```

## 📁 Project Structure

```
ahp_fce_topsis/
├── main.py                   # Main CLI application entry point
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── CLAUDE.md                # Development guidelines
├── modules/                 # Core algorithm implementations
│   ├── __init__.py
│   ├── ahp_module.py        # AHP weight calculation with CR validation
│   ├── fce_module.py        # Fuzzy comprehensive evaluation
│   ├── topsis_module.py     # TOPSIS ranking algorithm
│   ├── ga_optimizer.py      # Genetic algorithm optimization
│   └── evaluator.py         # Evaluation pipeline orchestration
├── utils/                   # Helper utilities
│   ├── __init__.py
│   ├── consistency_check.py # AHP consistency validation
│   ├── normalization.py     # Vector normalization utilities
│   ├── validation.py        # Schema and data validation
│   └── reporting.py         # Report generation system
├── config/                  # Configuration files
│   ├── indicators.yaml      # Indicator hierarchy with literature-based weights
│   ├── fuzzy_scale.yaml     # Fuzzy membership functions
│   └── scenarios/           # Optimization scenarios
├── data/                    # Input data
│   ├── expert_judgments/    # AHP comparison matrices
│   │   ├── primary_capabilities.yaml
│   │   └── secondary_indicators/
│   └── schemes/             # Combat system configurations
│       ├── balanced_force.yaml
│       ├── high_endurance_force.yaml
│       └── tech_lite_force.yaml
├── outputs/                 # Generated results (git-ignored)
│   ├── results/             # Evaluation and optimization results
│   ├── reports/             # Generated reports (markdown/PDF)
│   └── plots/               # Visualization outputs
└── tests/                   # Comprehensive test suite
    ├── unit/                # Unit tests for individual modules
    ├── integration/         # End-to-end integration tests
    └── fixtures/            # Test data and configurations
```

## 🎯 Available Schemes

The system includes three pre-configured force structures:

1. **Balanced Force** (`balanced_force.yaml`): Well-rounded multi-domain capability
2. **High Endurance Force** (`high_endurance_force.yaml`): Extended operations with superior sustainment
3. **Technology-Lite Force** (`tech_lite_force.yaml`): Cost-effective solution with modern capabilities

## 📊 Evaluation Capabilities

### Primary Capabilities (5 dimensions)
基于无人作战体系效能评估一级指标体系的设定：
- **C1**: 态势感知能力 (Situational Awareness Capability) - 作战体系的"眼睛"和"前脑"
- **C2**: 指挥决策能力 (Command & Decision Capability) - 作战体系的"神经中枢"
- **C3**: 行动打击能力 (Action & Strike Capability) - 作战体系"拳头"的最终体现
- **C4**: 网络通联能力 (Network & Communication Capability) - 作战体系的"血脉"
- **C5**: 体系生存能力 (System Survivability Capability) - 作战体系的"金钟罩"

### Secondary Indicators (15 metrics)
- **C1**: 侦察探测能力, 信息融合能力, 态势理解能力
- **C2**: 任务规划能力, 威胁评估能力, 决策响应能力
- **C3**: 火力打击能力, 机动占位能力, 电子对抗能力
- **C4**: 信息传输能力, 网络可靠性, 协同作战能力
- **C5**: 抗毁能力, 任务恢复能力, 持续作战能力

## 🔧 Configuration Options

### AHP Parameters
- Consistency ratio threshold: 0.1
- Supported matrix dimensions: 2-15
- Eigenvalue calculation method: Power iteration

### FCE Parameters
- Linguistic scale: 差 (0.25), 中 (0.50), 良 (0.75), 优 (1.00)
- Membership degree normalization: Sum-to-1 constraint
- Expert consensus aggregation: Weighted averaging

### TOPSIS Parameters
- Normalization method: Vector normalization
- Distance metric: Euclidean distance
- Ranking criterion: Relative closeness coefficient (Ci)

### GA Parameters
- Population size: 10-100 (configurable)
- Generations: 20-200 (configurable)
- Crossover rate: 0.6-0.9 (configurable)
- Mutation rate: 0.01-0.2 (configurable)

## 📈 Algorithm Details

### AHP (Analytic Hierarchy Process)
- **Method**: Eigenvalue decomposition with consistency validation
- **Validation**: Consistency Ratio (CR) < 0.1 required
- **Scope**: 5 primary capabilities and 15 secondary indicators
- **Implementation**: Power iteration method for eigenvalue calculation

### FCE (Fuzzy Comprehensive Evaluation)
- **Linguistic Scale**: 差 (0.25), 中 (0.50), 良 (0.75), 优 (1.00)
- **Processing**: Membership degree normalization and expert aggregation
- **Integration**: Qualitative assessments converted to quantitative scores
- **Application**: All 15 secondary indicators use fuzzy evaluation

### TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
- **Normalization**: Vector normalization of decision matrix
- **Distance**: Euclidean distance to positive (PIS) and negative (NIS) ideal solutions
- **Ranking**: Relative closeness coefficient (Ci) in range [0,1]
- **Output**: Ranked alternatives with performance scores

### GA (Genetic Algorithm Optimization)
- **Library**: PyGAD for robust optimization
- **Constraints**: Operational constraints enforced during evolution
- **Monitoring**: Real-time convergence tracking and fitness evaluation
- **Output**: Optimized platform configurations under budget/resource limits

## 🔍 Validation & Quality Assurance

### Validation Features
- **Sensitivity Analysis**: Configurable weight perturbation (default ±20%)
- **Jackknife Validation**: Systematic expert exclusion for robustness testing
- **Audit Trail**: Complete transformation chain logging with timestamps
- **Performance Monitoring**: Execution time tracking and convergence analysis

### Quality Metrics
- **AHP Consistency**: All matrices must satisfy CR < 0.1
- **FCE Normalization**: Membership degrees sum to 1.0
- **TOPSIS Scores**: Ci coefficients in valid range [0,1]
- **GA Convergence**: Fitness improvement monitoring

## 🧪 Testing

### Test Suite Coverage
- **Unit Tests**: Individual module testing (21 passing)
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Benchmarking and scalability validation
- **Data Validation**: Schema compliance and data integrity checks

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run unit tests only
python -m pytest tests/unit/ -v

# Run integration tests only
python -m pytest tests/integration/ -v

# Run with coverage
python -m pytest tests/ --cov=modules --cov-report=html
```

## 📊 Example Results

### Sample Evaluation Output
```
Starting evaluation...
Loaded 3 scheme(s) for evaluation

Evaluating scheme 1/3: balanced_force
  Ci Score: 0.5292
  Rank: 2
  Validation: PASSED

Evaluating scheme 2/3: high_endurance_force
  Ci Score: 0.5752
  Rank: 1
  Validation: PASSED

Evaluating scheme 3/3: tech_lite_force
  Ci Score: 0.4369
  Rank: 3
  Validation: PASSED

Evaluation completed successfully!
Best scheme: high_endurance_force (Ci: 0.5752)
```

## 🤝 Contributing

This is a research prototype focused on military systems evaluation. When contributing:

1. **Mathematical Rigor**: Ensure all implementations follow established theoretical foundations
2. **Validation**: Maintain CR < 0.1 for AHP matrices and proper normalization
3. **Documentation**: Update README and code comments for new features
4. **Testing**: Add appropriate unit and integration tests
5. **Code Style**: Follow Python PEP 8 guidelines

## 📄 License

This project is provided for research and educational purposes. Please ensure appropriate attribution for military systems evaluation research.

## 📚 References

### Core Methodology
- Saaty, T. L. (2008). *Decision making with the analytic hierarchy process*. International Journal of the Analytic Hierarchy Process.
- Hwang, C. L., & Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*. Springer-Verlag.
- Zadeh, L. A. (1965). *Fuzzy sets*. Information and Control.

### Military Systems Evaluation
- Alberts, D. S. (2000). *Network Centric Warfare: Developing and Leveraging Information Superiority*. CCRP.
- Boyd, J. R. (1987). *A Discourse on Winning and Losing*. USAF.
- NATO Standardization Office (2019). *Allied Joint Publication 3.9: Maritime Unmanned Systems*.

### Technical Implementation
- PyGAD Documentation (2023). *Genetic Algorithm in Python*.
- IEEE Standards (2020). *Radar and Sensor Performance Specifications*.
- Chinese DoD Research (2021). *Modern Naval Warfare Evaluation Standards*.