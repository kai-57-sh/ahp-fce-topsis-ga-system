# Quickstart Guide: AHP-FCE-TOPSIS-GA Evaluation System

**Purpose**: Get started with combat system evaluation and optimization in under 15 minutes

**Audience**: Military systems analysts, researchers, mission planners

---

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8, 3.9, 3.10, or 3.11
- **RAM**: 8GB minimum (16GB recommended for GA optimization)
- **Disk Space**: 500MB for dependencies and outputs

### Knowledge Requirements

- Basic familiarity with multi-criteria decision analysis (MCDA) concepts
- Understanding of AHP (Analytic Hierarchy Process) and pairwise comparisons
- Python experience helpful but not required for basic usage

---

## Installation

### Step 1: Clone and Navigate

```bash
git clone <repository-url>
cd ahp_fce_topsis
```

### Step 2: Create Virtual Environment

```bash
# Using venv (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n ahp_eval python=3.10
conda activate ahp_eval
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output**:
```
Successfully installed numpy-1.24.3 pandas-2.0.2 pygad-3.1.0 matplotlib-3.7.1 pyyaml-6.0 pytest-7.3.1
```

### Step 4: Verify Installation

```bash
python -c "import numpy, pandas, pygad, matplotlib, yaml; print('All dependencies installed successfully')"
```

---

## Usage Scenarios

### Scenario A: Evaluate Pre-defined Configurations (MVP)

**Goal**: Compare 3 baseline combat system configurations and identify the best one

**Time**: 5 minutes

#### Step 1: Prepare Configuration Data

The repository includes 3 sample configurations in `data/schemes/`:

- `baseline_scheme.yaml` - Standard configuration (3 USV-A, 2 USV-B, 4 UUV-A, 3 UUV-B)
- `scheme_a.yaml` - USV-heavy configuration (5 USV-A, 3 USV-B, 2 UUV-A, 2 UUV-B)
- `scheme_b.yaml` - UUV-heavy configuration (2 USV-A, 1 USV-B, 6 UUV-A, 5 UUV-B)

#### Step 2: Run Evaluation

```bash
python main.py evaluate --batch \
  --schemes data/schemes/baseline_scheme.yaml \
           data/schemes/scheme_a.yaml \
           data/schemes/scheme_b.yaml \
  --output outputs/results/comparison_001.json
```

**Expected output**:
```
[INFO] Loading configuration: config/indicators.yaml
[INFO] Loading fuzzy sets: config/fuzzy_sets.yaml
[INFO] Loading expert judgments: data/expert_judgments/
[INFO] Validating AHP matrices...
  ✓ primary_capabilities (CR=0.023 < 0.1)
  ✓ c1_indicators (CR=0.018 < 0.1)
  ✓ c2_indicators (CR=0.031 < 0.1)
  ✓ c3_indicators (CR=0.027 < 0.1)
  ✓ c4_indicators (CR=0.015 < 0.1)
  ✓ c5_indicators (CR=0.029 < 0.1)
[INFO] Evaluating 3 configurations...
[INFO] Baseline Scheme: Ci = 0.652
[INFO] Scheme A: Ci = 0.744
[INFO] Scheme B: Ci = 0.598
[INFO] Rankings:
  1. Scheme A (Ci=0.744)
  2. Baseline Scheme (Ci=0.652)
  3. Scheme B (Ci=0.598)
[INFO] Results saved to: outputs/results/comparison_001.json
[INFO] Audit log: outputs/results/audit_comparison_001.log
```

#### Step 3: View Results

```bash
# Pretty-print JSON results
python -m json.tool outputs/results/comparison_001.json
```

**Result structure**:
```json
[
  {
    "result_id": "eval_20251025_143245_001",
    "configuration_id": "scheme_a",
    "final_ci_score": 0.744,
    "rank": 1,
    "raw_indicator_values": [0.82, 2.1, 0.75, 2.8, 0.88, ...],
    "...": "..."
  },
  {
    "result_id": "eval_20251025_143245_002",
    "configuration_id": "baseline",
    "final_ci_score": 0.652,
    "rank": 2,
    "...": "..."
  },
  {
    "result_id": "eval_20251025_143245_003",
    "configuration_id": "scheme_b",
    "final_ci_score": 0.598,
    "rank": 3,
    "...": "..."
  }
]
```

#### Step 4: Generate Visualization

```bash
python main.py visualize \
  --results outputs/results/comparison_001.json \
  --output outputs/plots/comparison_chart.png
```

This generates a bar chart comparing Ci scores across configurations.

---

### Scenario B: Optimize Configuration with Genetic Algorithm

**Goal**: Find optimal platform mix and deployment for maximum effectiveness

**Time**: 8 minutes (including 5-minute GA run)

#### Step 1: Define Scenario and Constraints

Edit `config/scenarios/strait_control.yaml`:

```yaml
scenario_id: "strait_control"
description: "海峡封控作战场景"

constraints:
  max_budget: 50000000  # ¥50M
  max_platforms: 15
  min_coverage_area: 120  # km²
  deployment_bounds:
    x_min: 119.5
    x_max: 121.0
    y_min: 23.8
    y_max: 25.2

decision_variables:
  usv_type_a: {min: 0, max: 10}
  usv_type_b: {min: 0, max: 8}
  uuv_type_a: {min: 0, max: 12}
  uuv_type_b: {min: 0, max: 10}
  deploy_center_x: {min: 119.5, max: 121.0}
  deploy_center_y: {min: 23.8, max: 25.2}
```

#### Step 2: Run Genetic Algorithm Optimization

```bash
python main.py optimize \
  --scenario config/scenarios/strait_control.yaml \
  --population 20 \
  --generations 50 \
  --output outputs/results/ga_run_001.json
```

**Expected output**:
```
[INFO] Initializing genetic algorithm...
[INFO] Population size: 20, Generations: 50
[INFO] Constraints: max_budget=50000000, max_platforms=15, min_coverage=120
[INFO] Starting optimization...
[Generation 1/50] Best fitness: 0.623, Avg fitness: 0.512, Diversity: 0.87
[Generation 2/50] Best fitness: 0.648, Avg fitness: 0.531, Diversity: 0.82
[Generation 3/50] Best fitness: 0.671, Avg fitness: 0.554, Diversity: 0.78
...
[Generation 48/50] Best fitness: 0.812, Avg fitness: 0.743, Diversity: 0.45
[Generation 49/50] Best fitness: 0.818, Avg fitness: 0.751, Diversity: 0.42
[Generation 50/50] Best fitness: 0.824, Avg fitness: 0.758, Diversity: 0.39
[INFO] Optimization complete!
[INFO] Best solution found:
  Platform mix: 6 USV-A, 4 USV-B, 7 UUV-A, 5 UUV-B
  Deployment: (120.35, 24.62)
  Predicted effectiveness: Ci = 0.824
[INFO] Results saved to: outputs/results/ga_run_001.json
[INFO] Total runtime: 4 minutes 18 seconds
```

#### Step 3: Analyze Convergence

```bash
python main.py visualize \
  --ga-results outputs/results/ga_run_001.json \
  --plot-type convergence \
  --output outputs/plots/ga_convergence_001.png
```

This generates a convergence curve showing fitness improvement over generations.

#### Step 4: Extract Optimized Configuration

```bash
python main.py extract-config \
  --ga-results outputs/results/ga_run_001.json \
  --output data/schemes/optimized_scheme.yaml
```

Creates a new configuration file that can be re-evaluated or used as a baseline.

---

### Scenario C: Sensitivity Analysis (Research Validation)

**Goal**: Validate robustness of evaluation results under weight perturbation

**Time**: 3 minutes

#### Step 1: Run Sensitivity Analysis

```bash
python main.py sensitivity \
  --baseline-results outputs/results/comparison_001.json \
  --perturbation 0.20 \
  --iterations 100 \
  --output outputs/results/sensitivity_001.json
```

**Expected output**:
```
[INFO] Running sensitivity analysis...
[INFO] Perturbation: ±20% on all indicator weights
[INFO] Iterations: 100
[Iteration 1/100] Rankings: [1, 2, 3] (baseline: [1, 2, 3])
[Iteration 2/100] Rankings: [1, 2, 3] (baseline: [1, 2, 3])
...
[Iteration 98/100] Rankings: [2, 1, 3] (baseline: [1, 2, 3]) ⚠ Rank change detected
[Iteration 99/100] Rankings: [1, 2, 3] (baseline: [1, 2, 3])
[Iteration 100/100] Rankings: [1, 2, 3] (baseline: [1, 2, 3])

[INFO] Sensitivity Analysis Results:
  Rankings stable: 97/100 iterations (97%)
  Top-3 preserved: 100/100 iterations (100%)
  Max Ci variation: ±8.2%
[INFO] Conclusion: Rankings are ROBUST under ±20% weight perturbation
[INFO] Results saved to: outputs/results/sensitivity_001.json
```

#### Step 2: Interpret Results

- **Stability ≥ 80%**: Results are robust (meets SC-009 criterion)
- **Stability < 80%**: Review indicator weights, consider expert recalibration

---

## Common Workflows

### Workflow 1: Adding a New Configuration

```bash
# 1. Copy template
cp data/schemes/baseline_scheme.yaml data/schemes/my_scheme.yaml

# 2. Edit with your parameters
nano data/schemes/my_scheme.yaml

# 3. Validate configuration
python main.py validate --scheme data/schemes/my_scheme.yaml

# 4. Run evaluation
python main.py evaluate --schemes data/schemes/my_scheme.yaml
```

### Workflow 2: Updating Expert Judgments

```bash
# 1. Edit judgment matrix
nano data/expert_judgments/c1_indicators.yaml

# 2. Validate CR
python main.py validate --ahp-matrix data/expert_judgments/c1_indicators.yaml

# Expected output:
# ✓ Matrix is reciprocal
# ✓ CR = 0.035 < 0.1 (VALID)

# 3. Re-run evaluation with updated weights
python main.py evaluate --batch --schemes data/schemes/*.yaml
```

### Workflow 3: Exporting for Publication

```bash
# Generate comprehensive report
python main.py report \
  --results outputs/results/comparison_001.json \
  --include-methodology \
  --include-sensitivity \
  --format pdf \
  --output outputs/reports/evaluation_report.pdf
```

Report includes:
- Methodology section with citations
- Indicator hierarchy table with weights
- Configuration comparison table
- Visualization charts
- Sensitivity analysis results

---

## Configuration Files Reference

### Indicator Hierarchy (`config/indicators.yaml`)

```yaml
objective: "水面和水下无人作战体系综合作战效能"

primary_capabilities:
  C1:
    name: "态势感知能力"
    weight: 0.25  # From AHP calculation
    secondary_indicators:
      P1_1:
        name: "目标探测覆盖率"
        type: "benefit"  # Higher is better
        weight: 0.40
        fuzzy: false  # Quantitative indicator
```

**Key fields**:
- `type`: `benefit` (maximize) or `cost` (minimize)
- `fuzzy`: `true` for qualitative indicators using FCE
- `weight`: From AHP eigenvalue method (must sum to 1.0 per level)

### Fuzzy Sets (`config/fuzzy_sets.yaml`)

```yaml
linguistic_terms:
  差: 0.25  # Poor
  中: 0.50  # Average
  良: 0.75  # Good
  优: 1.00  # Excellent
```

### Expert Judgments (`data/expert_judgments/*.yaml`)

```yaml
matrix_id: "c1_indicators"
dimension: 3
matrix:
  - [1.0, 2.0, 1.5]
  - [0.5, 1.0, 0.8]
  - [0.67, 1.25, 1.0]
```

**Matrix interpretation**:
- `matrix[0][1] = 2.0`: P1_1 is twice as important as P1_2
- `matrix[1][0] = 0.5`: Reciprocal (P1_2 is half as important as P1_1)

---

## Troubleshooting

### Issue 1: AHP Consistency Ratio Too High

**Error**:
```
AHPConsistencyError: CR = 0.152 exceeds threshold of 0.1 for matrix 'c2_indicators'
```

**Solution**:
1. Review the pairwise comparisons in `data/expert_judgments/c2_indicators.yaml`
2. Check for logical inconsistencies (e.g., A > B > C but C > A)
3. Reduce extreme comparisons (avoid using 9.0 unless truly necessary)
4. Re-engage experts for clarification

### Issue 2: GA Optimization Not Converging

**Symptom**:
```
[Generation 50/50] Best fitness: 0.524, Avg fitness: 0.503, Diversity: 0.82
⚠ Warning: Diversity remains high (>0.7), population may not have converged
```

**Solutions**:
- Increase `num_generations` to 100
- Reduce `mutation_rate` from 0.2 to 0.1
- Check if constraints are too restrictive (may have no good solutions)

### Issue 3: Memory Error During GA

**Error**:
```
MemoryError: Unable to allocate array with shape (1000, 15)
```

**Solutions**:
- Reduce `population_size` from 20 to 10
- Close other applications
- Use batch processing if evaluating many schemes

### Issue 4: Indicator Values Out of Range

**Error**:
```
ValidationError: Indicator P3_2 has negative value (-1.5), violates constraints
```

**Solution**:
- Check simplified simulation formulas in scheme YAML
- Ensure all indicator calculations use absolute values or valid ranges
- Verify cost-type indicators are properly labeled

---

## Performance Benchmarks

### Expected Performance (on Standard Laptop)

| Operation | Input Size | Target Time | Typical Time |
|-----------|-----------|-------------|--------------|
| AHP weight calculation | 5×5 matrix | <1 second | ~0.3s |
| Single scheme evaluation | 15 indicators | <0.5 seconds | ~0.2s |
| Batch evaluation | 5 schemes | <2.5 seconds | ~1.1s |
| GA optimization | 50 gen × 20 pop | <5 minutes | ~4 min 15s |
| Sensitivity analysis | 100 iterations | <3 minutes | ~2 min 30s |

### Performance Tuning

If operations are slower than expected:

1. **Enable NumPy vectorization** (already default)
2. **Profile code**:
   ```bash
   python -m cProfile -o profile.stats main.py evaluate --schemes data/schemes/baseline_scheme.yaml
   python -m pstats profile.stats
   ```
3. **Check NumPy BLAS backend**:
   ```bash
   python -c "import numpy; numpy.show_config()"
   ```
   Should show optimized BLAS (OpenBLAS, MKL, or Accelerate)

---

## Next Steps

### For Analysts

1. **Customize indicator hierarchy** to match your specific evaluation needs
2. **Add domain-specific scenarios** to `config/scenarios/`
3. **Calibrate fuzzy scales** based on expert consensus

### For Researchers

1. **Implement advanced validation** (jackknife, bootstrap) in User Story 3
2. **Integrate complex simulation models** (replace simplified formulas)
3. **Extend to multi-objective optimization** (Pareto frontier analysis)

### For Developers

1. Review [data-model.md](./data-model.md) for entity schemas
2. Review [contracts/module_interfaces.md](./contracts/module_interfaces.md) for API reference
3. Run test suite: `pytest tests/`

---

## Additional Resources

- **Research documentation**: `specs/001-ahp-fce-topsis-ga-system/research.md`
- **Data model**: `specs/001-ahp-fce-topsis-ga-system/data-model.md`
- **Module contracts**: `specs/001-ahp-fce-topsis-ga-system/contracts/`
- **Project constitution**: `.specify/memory/constitution.md`

**Support**: Refer to project README.md for contribution guidelines and issue reporting.

---

**Quickstart Complete**: You're now ready to evaluate combat systems and run optimization! 🚀
