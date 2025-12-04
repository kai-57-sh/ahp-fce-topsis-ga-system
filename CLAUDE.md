# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an AHP-FCE-TOPSIS-GA hybrid multi-criteria decision analysis system for evaluating unmanned combat system configurations. The system combines four methodologies: Analytic Hierarchy Process (AHP), Fuzzy Comprehensive Evaluation (FCE), Technique for Order Preference by Similarity to Ideal Solution (TOPSIS), and Genetic Algorithm (GA) optimization.

## Commands

### Core System Operations
```bash
# System version and validation
python main.py --version
python main.py validate --scheme data/schemes/balanced_force.yaml
python main.py validate --ahp-matrix data/expert_judgments/primary_capabilities.yaml

# Single and batch evaluation
python main.py evaluate --schemes data/schemes/balanced_force.yaml --output results.json
python main.py evaluate --schemes data/schemes/*.yaml --batch --output batch_results.json

# Scenario-aware evaluation (v1.1.0+)
python main.py evaluate --schemes data/schemes/balanced_force.yaml --scenario data/scenarios/operational/nearshore_underwater_recon.yaml --output scenario_results.json

# Genetic algorithm optimization
python main.py optimize --scenario data/scenarios/operational/amphibious_landing_clearance.yaml --population 50 --generations 100 --output optimization.json

# Sensitivity analysis and visualization
python main.py sensitivity --baseline-results results.json --perturbation 0.2 --output sensitivity.json
python main.py visualize --plot-type convergence --input optimization.json --output convergence.png
python main.py visualize --plot-type comparison --input results.json --output comparison.png

# Report generation
python main.py report --results results.json --include-methodology --output report.md
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Validate installation
python main.py --version
```

### Testing
```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v  # Module-specific tests
python -m pytest tests/integration/ -v  # End-to-end workflow tests

# Coverage reporting
python -m pytest tests/ --cov=modules --cov-report=html

# Quick validation with single test
python -m pytest tests/unit/test_ahp.py::test_cr_calculation -v  # Test AHP consistency calculation
```

### Development Tools
```bash
# Code formatting and linting
black modules/ utils/ main.py
flake8 modules/ utils/ main.py

# Debug evaluation process
python debug_evaluation.py  # Run step-by-step debugging of single scheme evaluation
```

## Architecture Overview

### Core Evaluation Pipeline
The system follows a four-stage evaluation pipeline orchestrated by `modules/evaluator.py`:

1. **Scenario Integration** (Optional): Context-aware evaluation using operational scenarios
2. **AHP Weight Calculation**: Hierarchical weighting with consistency validation (CR < 0.1)
3. **Fuzzy Comprehensive Evaluation**: Qualitative-to-quantitative conversion using linguistic variables
4. **TOPSIS Ranking**: Multi-criteria decision analysis with relative closeness coefficients

### Key Modules
- **`modules/evaluator.py`**: Central orchestration of the AHP-FCE-TOPSIS pipeline
- **`modules/ahp_module.py`**: Analytic Hierarchy Process implementation with CR validation
- **`modules/fce_module.py`**: Fuzzy evaluation with linguistic scale processing
- **`modules/topsis_module.py`**: TOPSIS ranking algorithm implementation
- **`modules/ga_optimizer.py`**: Genetic algorithm optimization using PyGAD
- **`modules/scenario_integration.py`**: Scenario-aware evaluation adjustments

### Data Flow Architecture
```
Input Schemes → Scenario Integration → AHP Weights → Fuzzy Scores → TOPSIS Ranking → Results
                     ↓                                                    ↓
              Operational Constraints                                GA Optimization
```

### Configuration Structure
- **`config/indicators.yaml`**: Five-dimensional capability hierarchy (C1-C5) with literature-based weights
- **`config/fuzzy_sets.yaml`**: Linguistic scale definitions (差/中/良/优) and applicable indicators
- **`data/expert_judgments/`**: AHP comparison matrices for weight calculation (primary + secondary indicators)
- **`data/scenarios/`**: Operational scenarios for context-aware evaluation (v1.1.0+)
- **`data/schemes/`**: Combat system configurations to evaluate (platform inventories and capabilities)

#### Available Scheme Templates
- **`balanced_force.yaml`**: Well-rounded multi-domain capability (baseline)
- **`high_endurance_force.yaml`**: Extended operations with superior sustainment
- **`tech_lite_force.yaml`**: Cost-effective solution with modern capabilities
- **`template_scheme.yaml`**: Template for creating new configurations

### Critical Implementation Details

#### AHP Implementation
- Uses eigenvalue decomposition with power iteration method
- Enforces consistency ratio (CR) < 0.1 for all judgment matrices
- Supports 5 primary capabilities and 15 secondary indicators
- Automatic inconsistency detection and reporting

#### GA Optimization
- Chromosome encoding maps platform counts to operational scenarios
- Implements constraint-aware evolution with penalty functions
- Uses adaptive mutation rates based on convergence progress
- Generates convergence plots and detailed optimization reports

#### Scenario Integration (v1.1.0+)
- Dynamic indicator weight adjustment based on operational context
- Supports four operational scenarios: nearshore reconnaissance, strait control, amphibious landing, high-value blockade
- Provides 70%+ improvement in evaluation accuracy for scenario-specific assessments
- Each scenario has specific threat levels, success criteria, and operational constraints
- Scenario files define weight adjustments, environmental factors, and mission priorities

### Important Constraints
- AHP consistency ratio must be < 0.1 for valid weights
- Fuzzy membership degrees must sum to 1.0
- GA optimization respects budget and platform count constraints
- All evaluations require valid deployment plans and task assignments
- Scheme files must follow the exact schema in `data/schemes/template_scheme.yaml`
- Expert judgment matrices must be square with consistent dimensions (2-15)

### Output Structure
Results include:
- **Ci Scores**: TOPSIS relative closeness coefficients (0-1 range)
- **Rankings**: Comparative performance assessment
- **Audit Trails**: Complete transformation logging
- **Validation Reports**: Consistency and constraint satisfaction validation
- **Visualizations**: Convergence plots and comparison charts

### Testing Strategy
The system maintains comprehensive test coverage including:
- Unit tests for individual algorithm implementations
- Integration tests for end-to-end evaluation workflows
- Data validation tests for schema compliance
- Performance benchmarks for GA optimization

### Common Development Patterns
- All modules use structured exception handling with custom exception classes
- Configuration validation happens at multiple pipeline stages
- Audit logging tracks all data transformations for reproducibility
- Results are serialized to JSON with detailed metadata and validation status

### File Conventions
- **Scheme files**: YAML format following `template_scheme.yaml` structure with platform inventories
- **Expert judgments**: Hierarchical matrices in `data/expert_judgments/` (primary + secondary indicators)
- **Configuration files**: YAML format in `config/` directory with descriptive comments
- **Output files**: JSON format with validation metadata and audit trails
- **Test fixtures**: YAML files in `tests/fixtures/` for reproducible testing

### Debugging Workflow
1. Use `debug_evaluation.py` for step-by-step evaluation debugging
2. Run single module tests to isolate issues: `python -m pytest tests/unit/test_ahp.py -v`
3. Validate configuration files before running full evaluations
4. Check audit trails in JSON outputs for transformation details
5. Verify AHP consistency ratios (< 0.1) when encountering weight calculation errors