# Module Contracts: AHP-FCE-TOPSIS-GA Evaluation System

**Purpose**: Define function signatures and interfaces for all core modules

**Note**: This is a command-line Python tool, so contracts are Python function signatures rather than HTTP APIs. All modules expose programmatic interfaces for use by the evaluator and CLI.

---

## Contract 1: AHP Module (`modules/ahp_module.py`)

**Responsibility**: Calculate indicator weights from expert pairwise comparison matrices using eigenvalue method

### Function: `calculate_weights`

**Signature**:
```python
def calculate_weights(judgment_matrix: np.ndarray) -> dict:
    """
    Calculate normalized weights from AHP judgment matrix using eigenvalue method.

    Args:
        judgment_matrix: Square numpy array of pairwise comparisons (n×n)
                        Values typically in range [1/9, 9]
                        Must satisfy reciprocal property: A[i][j] = 1/A[j][i]

    Returns:
        dict containing:
            'weights': np.ndarray of normalized weights (sum = 1.0)
            'lambda_max': float, maximum eigenvalue
            'CR': float, Consistency Ratio
            'valid': bool, True if CR < 0.1

    Raises:
        ValueError: If matrix is not square or violates reciprocal property
        AHPConsistencyError: If CR >= 0.1

    Example:
        >>> matrix = np.array([[1.0, 2.0, 1.0],
        ...                    [0.5, 1.0, 0.5],
        ...                    [1.0, 2.0, 1.0]])
        >>> result = calculate_weights(matrix)
        >>> result['weights']
        array([0.4, 0.2, 0.4])
        >>> result['CR'] < 0.1
        True
    """
```

### Function: `validate_judgment_matrix`

**Signature**:
```python
def validate_judgment_matrix(matrix: np.ndarray, tolerance: float = 1e-6) -> bool:
    """
    Validate AHP judgment matrix satisfies required properties.

    Args:
        matrix: Square numpy array to validate
        tolerance: Numerical tolerance for reciprocal check

    Returns:
        bool: True if valid

    Raises:
        ValueError: If matrix violates properties (with specific error message)

    Checks:
        - Matrix is square (n×n)
        - Diagonal elements are 1.0
        - Reciprocal property: A[i][j] * A[j][i] ≈ 1.0
        - All elements > 0
    """
```

**Input Constraints**:
- Matrix dimension: 2 ≤ n ≤ 10 (practical limit)
- Element range: 1/9 ≤ A[i][j] ≤ 9 (Saaty scale)
- Reciprocal tolerance: 1e-6

**Output Guarantees**:
- Weights always sum to 1.0 (±1e-10)
- CR calculation uses standard Random Index (RI) values
- If CR ≥ 0.1, raises AHPConsistencyError

**Performance**:
- Target: <1 second for 5×5 matrix
- Complexity: O(n³) for eigenvalue decomposition

---

## Contract 2: FCE Module (`modules/fce_module.py`)

**Responsibility**: Convert qualitative expert assessments to quantified fuzzy scores

### Function: `fuzzy_evaluate`

**Signature**:
```python
def fuzzy_evaluate(
    expert_assessments: dict[str, int],
    fuzzy_scale: dict[str, float]
) -> dict:
    """
    Convert expert linguistic assessments to fuzzy score using FCE.

    Args:
        expert_assessments: Count of experts selecting each linguistic term
                           Example: {'差': 0, '中': 1, '良': 3, '优': 1}
        fuzzy_scale: Mapping of linguistic terms to quantified values
                    Example: {'差': 0.25, '中': 0.50, '良': 0.75, '优': 1.00}

    Returns:
        dict containing:
            'membership_vector': np.ndarray of normalized expert counts (sum = 1.0)
            'fuzzy_score': float in [0, 1], weighted average
            'consensus_level': float in [0, 1], measure of expert agreement

    Raises:
        ValueError: If assessments/scale mismatch or invalid values

    Example:
        >>> assessments = {'差': 0, '中': 1, '良': 3, '优': 1}
        >>> scale = {'差': 0.25, '中': 0.50, '良': 0.75, '优': 1.00}
        >>> result = fuzzy_evaluate(assessments, scale)
        >>> result['fuzzy_score']
        0.70
        >>> result['membership_vector']
        array([0.0, 0.2, 0.6, 0.2])
    """
```

### Function: `validate_membership_degrees`

**Signature**:
```python
def validate_membership_degrees(membership_vector: np.ndarray, tolerance: float = 1e-3) -> bool:
    """
    Validate fuzzy membership degrees satisfy normalization requirement.

    Args:
        membership_vector: Array of membership degrees
        tolerance: Acceptable deviation from sum = 1.0

    Returns:
        bool: True if valid

    Raises:
        ValueError: If sum deviates from 1.0 by more than tolerance
    """
```

**Input Constraints**:
- All expert counts ≥ 0
- At least 1 expert assessment total
- Fuzzy scale values in [0, 1], strictly increasing

**Output Guarantees**:
- Membership vector always sums to 1.0 (±1e-3)
- Fuzzy score in [0, 1]
- Consensus level: 1.0 = perfect agreement, 0.0 = uniform distribution

**Performance**:
- Target: <0.1 seconds for typical input (5 experts, 4 linguistic terms)
- Complexity: O(n) where n = number of linguistic terms

---

## Contract 3: TOPSIS Module (`modules/topsis_module.py`)

**Responsibility**: Rank configurations using TOPSIS method with weighted normalized values

### Function: `topsis_rank`

**Signature**:
```python
def topsis_rank(
    decision_matrix: np.ndarray,
    weights: np.ndarray,
    indicator_types: list[str]
) -> dict:
    """
    Rank configurations using TOPSIS method.

    Args:
        decision_matrix: 2D array (n_schemes × n_indicators) of indicator values
        weights: 1D array (n_indicators) of indicator weights (must sum to 1.0)
        indicator_types: List of 'benefit' or 'cost' for each indicator

    Returns:
        dict containing:
            'normalized_matrix': np.ndarray, vector-normalized values
            'weighted_matrix': np.ndarray, after applying weights
            'PIS': np.ndarray, positive ideal solution
            'NIS': np.ndarray, negative ideal solution
            'D_plus': np.ndarray, distances to PIS for each scheme
            'D_minus': np.ndarray, distances to NIS for each scheme
            'Ci': np.ndarray, relative closeness scores (higher is better)
            'rankings': np.ndarray, rank order (1 = best)

    Raises:
        ValueError: If matrix dimensions mismatch or weights don't sum to 1.0

    Example:
        >>> decision_matrix = np.array([[0.75, 2.5], [0.82, 1.8], [0.68, 3.1]])
        >>> weights = np.array([0.6, 0.4])
        >>> indicator_types = ['benefit', 'cost']
        >>> result = topsis_rank(decision_matrix, weights, indicator_types)
        >>> result['Ci']
        array([0.52, 0.68, 0.43])
        >>> result['rankings']
        array([2, 1, 3])
    """
```

### Function: `identify_ideal_solutions`

**Signature**:
```python
def identify_ideal_solutions(
    weighted_matrix: np.ndarray,
    indicator_types: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    """
    Identify PIS and NIS based on indicator types.

    Args:
        weighted_matrix: Weighted normalized decision matrix
        indicator_types: 'benefit' or 'cost' for each indicator

    Returns:
        tuple of (PIS, NIS) as 1D arrays

    Logic:
        - Benefit indicators: PIS = max, NIS = min
        - Cost indicators: PIS = min, NIS = max
    """
```

**Input Constraints**:
- Decision matrix: n_schemes ≥ 2, n_indicators ≥ 1
- Weights must sum to 1.0 (±1e-6)
- All indicator values > 0 (for vector normalization)
- indicator_types length must match n_indicators

**Output Guarantees**:
- Ci scores in [0, 1]
- Rankings are 1-indexed (1 = best)
- Normalized matrix preserves relative ordering within each indicator
- D_plus + D_minus > 0 (enforced in Ci calculation)

**Performance**:
- Target: <0.5 seconds for 10 schemes × 15 indicators
- Complexity: O(n × m) where n = schemes, m = indicators

---

## Contract 4: Evaluator (`modules/evaluator.py`)

**Responsibility**: Orchestrate full evaluation pipeline (AHP → FCE → TOPSIS)

### Function: `evaluate_single_scheme`

**Signature**:
```python
def evaluate_single_scheme(
    scheme_data: dict,
    indicator_config: dict,
    fuzzy_config: dict,
    expert_judgments: dict
) -> dict:
    """
    Evaluate a single combat system configuration.

    Args:
        scheme_data: Configuration data (from data/schemes/*.yaml)
        indicator_config: Indicator hierarchy with weights (from config/indicators.yaml)
        fuzzy_config: Fuzzy evaluation sets (from config/fuzzy_sets.yaml)
        expert_judgments: AHP matrices (from data/expert_judgments/*.yaml)

    Returns:
        dict containing EvaluationResult entity (see data-model.md):
            'result_id': str
            'configuration_id': str
            'raw_indicator_values': list[float]
            'normalized_values': list[float]
            'weighted_values': list[float]
            'topsis_metrics': dict
            'final_ci_score': float
            'timestamp': datetime
            'audit_log_path': str

    Raises:
        ValidationError: If any validation step fails

    Workflow:
        1. Extract indicator values from scheme_data
        2. Apply FCE to qualitative indicators
        3. Validate all 15 indicator values obtained
        4. Construct decision matrix (1 × 15)
        5. Apply TOPSIS normalization and weighting
        6. Calculate Ci score
        7. Generate audit log
    """
```

### Function: `evaluate_batch`

**Signature**:
```python
def evaluate_batch(
    schemes: list[dict],
    indicator_config: dict,
    fuzzy_config: dict,
    expert_judgments: dict
) -> list[dict]:
    """
    Evaluate multiple configurations and rank them.

    Args:
        schemes: List of configuration data dicts
        indicator_config: Same as evaluate_single_scheme
        fuzzy_config: Same as evaluate_single_scheme
        expert_judgments: Same as evaluate_single_scheme

    Returns:
        list[dict]: EvaluationResult dicts sorted by Ci (descending)
                   Each includes 'rank' field (1 = best)

    Workflow:
        1. Evaluate each scheme individually
        2. Construct decision matrix (n_schemes × 15)
        3. Run TOPSIS ranking across all schemes
        4. Assign ranks based on Ci scores
        5. Return sorted results
    """
```

**Input Constraints**:
- Scheme data must match CombatSystemConfiguration schema
- Indicator config must pass validation (weights sum to 1.0 at each level)
- Fuzzy config must define all qualitative indicators
- Expert judgments must have CR < 0.1

**Output Guarantees**:
- Audit log includes full transformation chain
- Result is reproducible (deterministic)
- Timestamp is ISO 8601 format
- All intermediate values preserved

**Performance**:
- Single scheme: <0.5 seconds (SC-004)
- Batch of 10 schemes: <5 seconds

---

## Contract 5: GA Optimizer (`modules/ga_optimizer.py`)

**Responsibility**: Genetic algorithm optimization using PyGAD library

### Function: `optimize_configuration`

**Signature**:
```python
def optimize_configuration(
    scenario_config: dict,
    ga_params: dict,
    constraints: dict,
    evaluator_instance: Evaluator
) -> dict:
    """
    Find optimal combat system configuration using genetic algorithm.

    Args:
        scenario_config: Scenario-specific parameters (from config/scenarios/*.yaml)
        ga_params: GA algorithm parameters:
            {
                'population_size': int,
                'num_generations': int,
                'parent_selection': str,
                'crossover_type': str,
                'mutation_type': str,
                'mutation_rate': float
            }
        constraints: Operational constraints:
            {
                'max_budget': float,
                'max_platforms': int,
                'min_coverage': float,
                'deployment_bounds': dict
            }
        evaluator_instance: Evaluator object for fitness function

    Returns:
        dict containing OptimizationRun entity (see data-model.md):
            'run_id': str
            'scenario_id': str
            'algorithm_params': dict
            'constraints': dict
            'generation_history': list[dict]
            'final_best_solution': dict
            'termination_reason': str
            'execution_metadata': dict

    Raises:
        ConstraintError: If no feasible solution exists
        ValidationError: If GA params invalid

    Workflow:
        1. Initialize population (random valid chromosomes)
        2. For each generation:
            a. Evaluate fitness (call evaluator)
            b. Select parents
            c. Apply crossover
            d. Apply mutation
            e. Validate constraints
            f. Log metrics (best/avg/diversity)
        3. Return best solution found
    """
```

### Function: `fitness_function`

**Signature**:
```python
def fitness_function(
    ga_instance: pygad.GA,
    solution: np.ndarray,
    solution_idx: int
) -> float:
    """
    Fitness function for PyGAD integration.

    Args:
        ga_instance: PyGAD GA object (required by PyGAD API)
        solution: Chromosome (gene values)
        solution_idx: Index in population (required by PyGAD API)

    Returns:
        float: Fitness score (Ci value from TOPSIS evaluation)

    Workflow:
        1. Decode chromosome to configuration parameters
        2. Validate constraints
        3. Generate indicator values (simplified simulation)
        4. Call evaluator.evaluate_single_scheme()
        5. Return Ci score
    """
```

### Function: `decode_chromosome`

**Signature**:
```python
def decode_chromosome(chromosome: np.ndarray, gene_config: dict) -> dict:
    """
    Decode chromosome genes to configuration parameters.

    Args:
        chromosome: Array of gene values
        gene_config: Mapping of gene indices to parameter names/types

    Returns:
        dict: CombatSystemConfiguration format

    Example:
        >>> chromosome = np.array([5, 8, 120.3, 24.5, 2])
        >>> gene_config = {
        ...     0: {'name': 'usv_type_a', 'type': 'int'},
        ...     1: {'name': 'uuv_type_b', 'type': 'int'},
        ...     2: {'name': 'deploy_x', 'type': 'float'},
        ...     3: {'name': 'deploy_y', 'type': 'float'},
        ...     4: {'name': 'patrol_mode', 'type': 'int'}
        ... }
        >>> decode_chromosome(chromosome, gene_config)
        {
            'platform_inventory': {'usv_type_a': 5, 'uuv_type_b': 8},
            'deployment_plan': {'center_coordinates': [120.3, 24.5]},
            'task_assignments': {'patrol_mode': 2}
        }
    """
```

**Input Constraints**:
- GA params: population_size ≥ 10, num_generations ≥ 1, 0 ≤ mutation_rate ≤ 1
- Chromosomes must satisfy constraints at all times
- Evaluator must be properly initialized

**Output Guarantees**:
- Best solution satisfies 100% of constraints (SC-007)
- Generation history includes best/avg/diversity for each generation
- Diversity metric: 0.3 threshold maintained (SC-008)
- Optimization completes in <5 minutes (SC-006)

**Performance**:
- Target: 50 generations × 20 population = 1000 fitness evaluations
- With 0.5s per evaluation: <500 seconds total (within 5-minute limit)

---

## Contract 6: Validation Utilities (`utils/validation.py`)

**Responsibility**: Mathematical validation and audit logging

### Function: `log_transformation`

**Signature**:
```python
def log_transformation(
    stage: str,
    input_data: np.ndarray,
    output_data: np.ndarray,
    metadata: dict
) -> str:
    """
    Log a transformation step for audit trail.

    Args:
        stage: Transformation stage name (e.g., 'normalization', 'weighting')
        input_data: Data before transformation
        output_data: Data after transformation
        metadata: Additional context (weights, parameters, etc.)

    Returns:
        str: Path to append log file

    Format:
        [2025-10-25 14:23:45] STAGE: normalization
        INPUT: [0.75, 2.5, 0.70, ...]
        OUTPUT: [0.55, 0.42, 0.48, ...]
        METADATA: {'method': 'vector_normalization', 'norm': [1.36, 5.91, ...]}
    """
```

### Function: `validate_evaluation_result`

**Signature**:
```python
def validate_evaluation_result(result: dict) -> bool:
    """
    Validate EvaluationResult entity against schema.

    Args:
        result: EvaluationResult dict

    Returns:
        bool: True if valid

    Raises:
        ValidationError: With specific field/constraint violation

    Checks:
        - All required fields present
        - Indicator value arrays length = 15
        - Ci score in [0, 1]
        - Timestamp format valid
        - Audit log file exists
    """
```

**Input Constraints**: N/A (utility functions)

**Output Guarantees**:
- Audit logs are append-only
- Validation errors are actionable (specify field and violation)
- Timestamps are UTC ISO 8601 format

---

## Contract Summary

| Module | Main Functions | Input | Output | Performance Target |
|--------|---------------|-------|--------|-------------------|
| AHP | `calculate_weights` | Judgment matrix (n×n) | Weights + CR | <1s for 5×5 |
| FCE | `fuzzy_evaluate` | Expert assessments + scale | Fuzzy score | <0.1s |
| TOPSIS | `topsis_rank` | Decision matrix + weights | Ci scores + rankings | <0.5s for 10×15 |
| Evaluator | `evaluate_single_scheme` | Scheme + configs | EvaluationResult | <0.5s |
| GA Optimizer | `optimize_configuration` | Scenario + params + constraints | OptimizationRun | <5min for 50gen |
| Validation | `log_transformation` | Stage + data + metadata | Log file path | <0.01s |

**Design Principles**:
- All functions are pure (no side effects except logging)
- Validation happens at module boundaries
- Errors are fail-fast with actionable messages
- All numeric results are reproducible (deterministic)
- Performance targets align with success criteria (SC-004, SC-006)

**Phase 1 Completion**: ✅ Contracts fully specified, ready for quickstart guide
