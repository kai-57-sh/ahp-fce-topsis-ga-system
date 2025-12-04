# Research: AHP-FCE-TOPSIS-GA Evaluation System

**Phase**: 0 (Outline & Research)
**Created**: 2025-10-25
**Purpose**: Resolve technical decisions and document best practices for implementation

## Research Questions Addressed

This research phase investigates:
1. **AHP Implementation**: How to implement eigenvalue method for weight calculation and CR validation
2. **FCE Integration**: Best practices for fuzzy membership function implementation in Python
3. **TOPSIS Algorithm**: Vector normalization approaches and ideal solution calculation
4. **GA Integration**: PyGAD library usage patterns and fitness function design
5. **Configuration Management**: YAML vs JSON for hierarchical indicator data
6. **Performance Optimization**: NumPy vectorization strategies for batch evaluation

---

## Decision 1: AHP Weight Calculation Method

**Decision**: Use eigenvalue method (principal eigenvector of judgment matrix)

**Rationale**:
- **Theoretical foundation**: Saaty (2008) establishes eigenvalue method as standard for AHP
- **Consistency with literature**: All referenced papers (吴汉荣 2007, 李大鹏 2012) use eigenvalue approach
- **NumPy support**: `numpy.linalg.eig()` provides efficient, tested implementation
- **CR calculation**: Consistency Index (CI) and Consistency Ratio (CR) formulas require maximum eigenvalue (λ_max)

**Alternatives considered**:
- **Geometric mean method**: Simpler but less theoretically rigorous, not suitable for research-grade output
- **Arithmetic mean of normalized columns**: Approximation only valid for perfectly consistent matrices

**Implementation approach**:
```python
# Using NumPy for eigenvalue decomposition
eigenvalues, eigenvectors = np.linalg.eig(judgment_matrix)
max_eigenvalue = np.max(eigenvalues.real)
principal_eigenvector = eigenvectors[:, np.argmax(eigenvalues.real)].real
weights = principal_eigenvector / np.sum(principal_eigenvector)

# CR calculation
n = len(judgment_matrix)
CI = (max_eigenvalue - n) / (n - 1)
CR = CI / RI[n]  # RI = Random Index lookup table
```

**References**:
- Saaty, T. L. (2008). Decision making with the analytic hierarchy process. *International journal of services sciences*, 1(1), 83-98.
- NumPy documentation: `numpy.linalg.eig` (https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html)

---

## Decision 2: Fuzzy Membership Function Representation

**Decision**: Use discrete membership vectors (not continuous functions)

**Rationale**:
- **Simplicity**: 4-level linguistic scale (差/中/良/优) maps to fixed scores [0.25, 0.50, 0.75, 1.0]
- **Expert input format**: Easier for domain experts to provide discrete assessments than continuous functions
- **Computational efficiency**: No need for function evaluation, direct vector operations
- **Literature alignment**: Hatami-Marbini & Kangi (2017) uses discrete fuzzy numbers for group decision making

**Alternatives considered**:
- **Triangular/trapezoidal fuzzy numbers**: More expressive but adds complexity without clear benefit for prototype
- **Gaussian membership functions**: Continuous but requires parameter tuning (mean, std dev) per indicator

**Implementation approach**:
```python
# Configuration in fuzzy_sets.yaml
fuzzy_scale:
  差: 0.25   # Poor
  中: 0.50   # Average
  良: 0.75   # Good
  优: 1.00   # Excellent

# Expert assessments stored as counts
expert_assessments:
  indicator_P1_1:
    差: 0
    中: 1
    良: 3
    优: 1

# Convert to membership degree vector
membership_vector = [0, 0.2, 0.6, 0.2]  # normalized counts

# Defuzzification (weighted average)
fuzzy_score = sum(membership_vector[i] * score_values[i] for i in range(4))
```

**References**:
- Hatami-Marbini, A., & Kangi, F. (2017). An extension of fuzzy TOPSIS for a group decision making. *Expert Systems with Applications*, 86, 221-230.
- Zadeh, L. A. (1965). Fuzzy sets. *Information and control*, 8(3), 338-353.

---

## Decision 3: TOPSIS Normalization Method

**Decision**: Vector normalization (Euclidean norm)

**Rationale**:
- **Standard practice**: Most widely used normalization in TOPSIS literature
- **Scale independence**: Eliminates units without distorting relative differences
- **NumPy vectorization**: Efficient implementation via `np.linalg.norm()`
- **Preserves ranking**: Maintains monotonicity of original indicator values

**Alternatives considered**:
- **Linear normalization (min-max)**: Can be affected by outliers, range [0,1] but loses distance information
- **Standardization (z-score)**: Negative values complicate interpretation of ideal solutions

**Implementation approach**:
```python
# Vector normalization for TOPSIS
decision_matrix = np.array(indicator_values)  # shape: (n_schemes, n_indicators)

# Normalize each column (indicator)
norms = np.linalg.norm(decision_matrix, axis=0)
normalized_matrix = decision_matrix / norms

# Apply weights
weighted_matrix = normalized_matrix * weights

# Identify ideal solutions
PIS = np.max(weighted_matrix, axis=0)  # for benefit-type indicators
NIS = np.min(weighted_matrix, axis=0)  # for benefit-type indicators
# (reverse for cost-type indicators based on config)

# Calculate distances
D_plus = np.linalg.norm(weighted_matrix - PIS, axis=1)
D_minus = np.linalg.norm(weighted_matrix - NIS, axis=1)

# Relative closeness
Ci = D_minus / (D_plus + D_minus)
```

**References**:
- Hwang, C. L., & Yoon, K. (1981). *Multiple attribute decision making: methods and applications*. Springer.
- NumPy documentation: `numpy.linalg.norm`

---

## Decision 4: PyGAD Integration Strategy

**Decision**: Use PyGAD's `GA` class with custom fitness function calling evaluation pipeline

**Rationale**:
- **Mature library**: PyGAD 3.0+ is actively maintained, well-documented, widely used
- **Flexible fitness function**: Supports arbitrary Python functions, allowing seamless integration with evaluator
- **Built-in operators**: Provides tournament/roulette selection, multiple crossover/mutation methods
- **Progress tracking**: Built-in callbacks for monitoring convergence, diversity metrics
- **No reinvention**: Avoids implementing GA from scratch (violates Rapid Prototyping principle)

**Alternatives considered**:
- **DEAP library**: More powerful but steeper learning curve, overkill for prototype
- **Scipy.optimize.differential_evolution**: Not a true GA, limited control over genetic operators
- **Custom implementation**: Violates Constitutional Principle IV (rapid prototyping)

**Implementation approach**:
```python
import pygad

def fitness_function(ga_instance, solution, solution_idx):
    """
    Fitness function interface between GA and evaluation pipeline.

    Args:
        solution: Chromosome encoding (e.g., [num_usv, num_uuv, deploy_x, deploy_y, ...])

    Returns:
        Ci score from TOPSIS evaluation (higher is better)
    """
    # Decode chromosome to configuration parameters
    config_params = decode_chromosome(solution)

    # Generate indicator values via simplified simulation
    indicator_values = simulate_scheme(config_params)

    # Run evaluation pipeline (AHP-FCE-TOPSIS)
    result = evaluator.evaluate_single_scheme(indicator_values)

    return result['Ci']  # Return fitness score

# Configure GA
ga_instance = pygad.GA(
    num_generations=50,
    num_parents_mating=4,
    fitness_func=fitness_function,
    sol_per_pop=20,
    num_genes=5,  # Example: [num_usv, num_uuv, deploy_x, deploy_y, patrol_mode]
    gene_space=[range(11), range(16), range(101), range(101), range(4)],
    mutation_percent_genes=20,
    parent_selection_type="tournament",
    crossover_type="single_point",
    mutation_type="random"
)

# Run optimization
ga_instance.run()

# Retrieve results
best_solution, best_fitness, _ = ga_instance.best_solution()
```

**References**:
- PyGAD documentation: https://pygad.readthedocs.io/
- PyGAD GitHub: https://github.com/ahmedfgad/GeneticAlgorithmPython

---

## Decision 5: Configuration File Format

**Decision**: YAML for all configuration files

**Rationale**:
- **Human-readable**: Experts can edit judgment matrices and fuzzy sets directly in text editor
- **Comments support**: Inline citations and methodology notes can be embedded (JSON doesn't support comments)
- **Hierarchical data**: Natural representation of indicator hierarchy (C1 → P1.1, P1.2, P1.3)
- **Python ecosystem**: `pyyaml` library is standard, well-maintained

**Alternatives considered**:
- **JSON**: More compact but lacks comments, harder for non-programmers to edit
- **TOML**: Good for flat configs but less intuitive for deep hierarchies
- **Python dictionaries**: Hard to version control, requires code changes to update data

**Configuration structure example**:
```yaml
# config/indicators.yaml
objective: "水面和水下无人作战体系综合作战效能"

primary_capabilities:
  C1:
    name: "态势感知能力"
    weight: 0.25  # From AHP
    reference: "Alberts et al. 2000, Boyd 1987"
    secondary_indicators:
      P1_1:
        name: "目标探测覆盖率"
        unit: "%"
        type: "benefit"  # Higher is better
        weight: 0.40  # Within C1
        reference: "OODA环理论 Observe环节"
      P1_2:
        name: "多源信息融合时效性"
        unit: "秒"
        type: "cost"  # Lower is better
        weight: 0.30
      P1_3:
        name: "态势理解准确性"
        unit: "定性"
        type: "benefit"
        weight: 0.30
        fuzzy: true  # Uses FCE
```

**References**:
- PyYAML documentation: https://pyyaml.org/wiki/PyYAMLDocumentation

---

## Decision 6: Performance Optimization Strategy

**Decision**: NumPy vectorization for batch evaluation

**Rationale**:
- **Performance requirement**: SC-004 requires <0.5s per configuration evaluation
- **Batch processing**: GA evaluates 20 configurations per generation × 50 generations = 1000 evaluations
- **NumPy efficiency**: Vectorized operations are 10-100× faster than Python loops
- **Memory constraints**: SC-006 requires <5 minutes total, so per-evaluation cost critical

**Implementation approach**:
```python
# SLOW: Loop over configurations
for scheme in schemes:
    for indicator in indicators:
        normalized[scheme][indicator] = scheme[indicator] / norm[indicator]

# FAST: Vectorized with NumPy
decision_matrix = np.array([[scheme[ind] for ind in indicators] for scheme in schemes])
norms = np.linalg.norm(decision_matrix, axis=0)
normalized_matrix = decision_matrix / norms  # Broadcasts automatically

# Additional optimizations:
# 1. Precompute AHP weights once (not per scheme)
# 2. Cache Random Index (RI) lookup table for CR calculation
# 3. Use np.einsum for weighted normalization if needed
# 4. Profile with cProfile to identify bottlenecks
```

**Performance validation**:
- Unit test with 10 schemes × 15 indicators should complete <50ms
- GA optimization (1000 evaluations) should complete <5 minutes per SC-006

**References**:
- NumPy performance guide: https://numpy.org/doc/stable/user/basics.performance.html

---

## Decision 7: Error Handling Strategy

**Decision**: Fail-fast validation at module boundaries

**Rationale**:
- **Scientific rigor**: Invalid inputs (CR ≥ 0.1, membership degrees not summing to 1.0) must be rejected immediately
- **Clear error messages**: FR-025 requires actionable error messages
- **Debugging efficiency**: Early detection prevents cascading errors in pipeline

**Validation points**:
1. **AHP module input**: Check judgment matrix is square, positive, reciprocal (A[i][j] = 1/A[j][i])
2. **AHP module output**: Validate CR < 0.1, weights sum to 1.0
3. **FCE module input**: Check membership degrees sum to 1.0 for each indicator
4. **TOPSIS module input**: Check indicator types (benefit/cost) specified for all indicators
5. **GA chromosome**: Validate constraints (platform counts ≥ 0, within budget) before evaluation

**Implementation pattern**:
```python
def validate_judgment_matrix(matrix, tolerance=1e-6):
    """Validate AHP judgment matrix properties."""
    n = len(matrix)

    # Check square
    if not all(len(row) == n for row in matrix):
        raise ValueError("Judgment matrix must be square")

    # Check reciprocal property
    for i in range(n):
        for j in range(n):
            if abs(matrix[i][j] * matrix[j][i] - 1.0) > tolerance:
                raise ValueError(
                    f"Reciprocal violation at ({i},{j}): "
                    f"{matrix[i][j]} * {matrix[j][i]} != 1.0"
                )

    return True
```

**References**:
- Python exception handling best practices

---

## Technology Stack Summary

### Core Dependencies

| Library | Version | Purpose | Installation |
|---------|---------|---------|--------------|
| numpy | ≥1.21 | Matrix operations, eigenvalue decomposition | `pip install numpy>=1.21` |
| pandas | ≥1.3 | Data structures for results tables | `pip install pandas>=1.3` |
| pygad | ≥3.0 | Genetic algorithm optimization | `pip install pygad>=3.0` |
| matplotlib | ≥3.5 | Visualization (convergence curves, charts) | `pip install matplotlib>=3.5` |
| pyyaml | ≥6.0 | YAML configuration parsing | `pip install pyyaml>=6.0` |
| pytest | ≥7.0 | Unit and integration testing | `pip install pytest>=7.0` |

### Optional Dependencies

| Library | Version | Purpose | When Needed |
|---------|---------|---------|-------------|
| scipy | ≥1.7 | Advanced statistical validation (jackknife) | User Story 3 (sensitivity analysis) |
| seaborn | ≥0.11 | Enhanced visualization aesthetics | Academic publication figures |
| jupyter | ≥1.0 | Interactive exploration during development | Development phase only |

### Development Environment

- **Python version**: 3.8, 3.9, 3.10, or 3.11 (recommend 3.10 for best compatibility)
- **Virtual environment**: `venv` or `conda` recommended to isolate dependencies
- **IDE**: VS Code with Python extension, or PyCharm
- **Version control**: Git (already initialized)

---

## Best Practices Summary

### Code Organization

1. **Module independence**: Each module (`ahp_module.py`, `fce_module.py`, etc.) should be importable and testable independently
2. **Configuration-driven**: All domain knowledge (indicators, weights, fuzzy sets) in YAML, not hardcoded
3. **Validation first**: Validate inputs before computation, fail fast with clear error messages
4. **Audit logging**: Log all transformations (raw → normalized → weighted → Ci) for reproducibility

### Testing Strategy

1. **Unit tests**: Test each module with known inputs/outputs from literature examples
2. **Integration tests**: Test full evaluation pipeline with sample schemes
3. **Validation tests**: Verify mathematical properties (CR < 0.1, weights sum to 1.0, etc.)
4. **Performance tests**: Ensure SC-004 (<0.5s) and SC-006 (<5min) targets met

### Documentation Requirements

1. **Docstrings**: All functions must include:
   - Purpose and methodology reference
   - Parameter types and constraints
   - Return value description
   - Example usage
2. **Configuration comments**: YAML files must cite literature sources for parameter choices
3. **README**: Setup instructions, example usage, performance expectations

---

## Phase 0 Completion Checklist

- [x] AHP implementation method selected (eigenvalue method)
- [x] FCE membership function approach decided (discrete vectors)
- [x] TOPSIS normalization technique chosen (vector normalization)
- [x] GA integration strategy defined (PyGAD with custom fitness function)
- [x] Configuration format selected (YAML)
- [x] Performance optimization strategy identified (NumPy vectorization)
- [x] Error handling approach established (fail-fast validation)
- [x] All alternatives considered and documented
- [x] Technology stack finalized
- [x] Best practices documented

**Status**: ✅ **Ready for Phase 1 (Design & Contracts)**
