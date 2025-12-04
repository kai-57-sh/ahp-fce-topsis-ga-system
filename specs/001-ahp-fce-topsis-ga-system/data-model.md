# Data Model: AHP-FCE-TOPSIS-GA Evaluation System

**Phase**: 1 (Design & Contracts)
**Created**: 2025-10-25
**Purpose**: Define data structures for indicators, configurations, evaluations, and optimization results

## Overview

This document defines the data model for the combat system evaluation system. All entities are represented as Python dictionaries/dataclasses in code and YAML/JSON in configuration/persistence. The model supports the complete workflow: expert judgment → weight calculation → scheme evaluation → optimization → results reporting.

---

## Entity 1: Indicator Hierarchy

**Purpose**: Represents the 5-level evaluation structure (Objective → C1-C5 Primary Capabilities → P1.1-P5.3 Secondary Indicators)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `objective` | string | required | Overall evaluation goal (fixed: "水面和水下无人作战体系综合作战效能") |
| `primary_capabilities` | dict | required, 5 items | Map of C1-C5 capability IDs to PrimaryCapability objects |

**PrimaryCapability Sub-entity**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | string | required, pattern: `C[1-5]` | Unique capability identifier (C1, C2, C3, C4, C5) |
| `name` | string | required | Chinese name (e.g., "态势感知能力") |
| `weight` | float | 0.0 < weight ≤ 1.0 | Relative importance (sum across C1-C5 must = 1.0) |
| `reference` | string | required | Literature citation (e.g., "Alberts et al. 2000, Boyd 1987") |
| `secondary_indicators` | dict | required, 3 items | Map of P*.* indicator IDs to SecondaryIndicator objects |

**SecondaryIndicator Sub-entity**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | string | required, pattern: `P[1-5]_[1-3]` | Unique indicator ID (e.g., P1_1, P1_2, P1_3) |
| `name` | string | required | Chinese name (e.g., "目标探测覆盖率") |
| `unit` | string | required | Measurement unit (e.g., "%", "秒", "定性") |
| `type` | enum | required, values: `benefit` or `cost` | Higher is better (benefit) vs. lower is better (cost) |
| `weight` | float | 0.0 < weight ≤ 1.0 | Relative importance within parent capability (sum = 1.0 per capability) |
| `reference` | string | required | Theoretical source (e.g., "OODA环理论 Observe环节") |
| `fuzzy` | boolean | required | True if qualitative (uses FCE), False if quantitative |

**Validation Rules**:
1. Exactly 5 primary capabilities (C1-C5)
2. Exactly 3 secondary indicators per primary capability (15 total)
3. Primary capability weights must sum to 1.0 (±0.001 tolerance)
4. Secondary indicator weights within each capability must sum to 1.0 (±0.001 tolerance)
5. All references must be non-empty strings
6. Quantitative (60%) vs. qualitative (40%) indicator ratio per constitutional requirement

**State Transitions**: N/A (static configuration, loaded at startup)

**Example (YAML)**:
```yaml
objective: "水面和水下无人作战体系综合作战效能"

primary_capabilities:
  C1:
    id: "C1"
    name: "态势感知能力"
    weight: 0.25
    reference: "Alberts et al. 2000, Boyd 1987"
    secondary_indicators:
      P1_1:
        id: "P1_1"
        name: "目标探测覆盖率"
        unit: "%"
        type: "benefit"
        weight: 0.40
        reference: "OODA环理论 Observe环节"
        fuzzy: false
      P1_2:
        id: "P1_2"
        name: "多源信息融合时效性"
        unit: "秒"
        type: "cost"
        weight: 0.30
        reference: "网络中心战 Information Superiority"
        fuzzy: false
      P1_3:
        id: "P1_3"
        name: "态势理解准确性"
        unit: "定性"
        type: "benefit"
        weight: 0.30
        reference: "OODA环理论 Orient环节"
        fuzzy: true
```

**File Location**: `config/indicators.yaml`

---

## Entity 2: Combat System Configuration

**Purpose**: Represents a specific force structure design (platform mix, deployment, task assignments)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | string | required, unique | Configuration identifier (e.g., "baseline", "scheme_a") |
| `name` | string | required | Human-readable name (e.g., "基线方案", "方案A") |
| `description` | string | optional | Purpose and design rationale |
| `platform_inventory` | dict | required | Platform counts by type |
| `deployment_plan` | dict | required | Geographic deployment |
| `task_assignments` | dict | required | Platform-to-mission mapping |
| `constraints` | dict | optional | Operational constraints |
| `metadata` | dict | optional | Author, date, scenario context |

**Platform Inventory Sub-structure**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `usv_type_a` | integer | ≥ 0 | Count of USV Type A platforms |
| `usv_type_b` | integer | ≥ 0 | Count of USV Type B platforms |
| `uuv_type_a` | integer | ≥ 0 | Count of UUV Type A platforms |
| `uuv_type_b` | integer | ≥ 0 | Count of UUV Type B platforms |

**Deployment Plan Sub-structure**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `deployment_zone` | string | required | Zone ID (e.g., "zone_1", "zone_2") |
| `center_coordinates` | array[2] | required, [x, y] within bounds | Deployment center [longitude, latitude] or [x, y] in simulation space |
| `radius` | float | > 0 | Deployment dispersion radius (km or simulation units) |

**Task Assignments Sub-structure**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `reconnaissance` | array[string] | optional | Platform IDs assigned to reconnaissance |
| `strike` | array[string] | optional | Platform IDs assigned to strike missions |
| `relay` | array[string] | optional | Platform IDs assigned to communication relay |

**Validation Rules**:
1. At least one platform must be specified (total count > 0)
2. Deployment coordinates must be within scenario bounds
3. Task assignments must reference valid platform IDs from inventory
4. Total cost (if constraints specified) must not exceed budget

**State Transitions**: Immutable once created (new configurations created for variations)

**Example (YAML)**:
```yaml
id: "baseline"
name: "基线方案"
description: "标准配置，用于性能对比基准"

platform_inventory:
  usv_type_a: 3
  usv_type_b: 2
  uuv_type_a: 4
  uuv_type_b: 3

deployment_plan:
  deployment_zone: "zone_1"
  center_coordinates: [120.5, 24.3]  # Longitude, Latitude
  radius: 5.0  # km

task_assignments:
  reconnaissance: ["usv_a_1", "usv_a_2", "uuv_a_1", "uuv_a_2"]
  strike: ["usv_b_1", "usv_b_2", "uuv_b_1"]
  relay: ["usv_a_3", "uuv_a_3", "uuv_a_4", "uuv_b_2", "uuv_b_3"]

constraints:
  max_budget: 50000000  # ¥50M
  max_total_platforms: 20
  coverage_area_required: 100  # km²

metadata:
  author: "系统分析员"
  created: "2025-10-25"
  scenario: "strait_control"
```

**File Location**: `data/schemes/*.yaml`

---

## Entity 3: Expert Judgment Matrix

**Purpose**: Stores pairwise comparison data from AHP process for weight calculation

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `matrix_id` | string | required, unique | Identifier (e.g., "primary_capabilities", "c1_indicators") |
| `expert_id` | string | required | Expert identifier for traceability |
| `comparison_scope` | string | required | What is being compared (e.g., "C1-C5 primary capabilities") |
| `dimension` | integer | required, ≥ 2 | Matrix size (5 for primary, 3 for secondary) |
| `matrix` | array[array[float]] | required, square, reciprocal | Pairwise comparison values (typically 1-9 scale) |
| `calculated_cr` | float | computed, ≥ 0 | Consistency Ratio (must be < 0.1) |
| `weights` | array[float] | computed, sum = 1.0 | Principal eigenvector (normalized weights) |
| `validation_status` | enum | required, values: `pending`, `valid`, `invalid` | Result of CR check |

**Matrix Format**:
- `matrix[i][j]`: Importance of element `i` relative to element `j`
- Scale: 1 (equal), 3 (moderate), 5 (strong), 7 (very strong), 9 (extreme)
- Reciprocal: `matrix[i][j] = 1 / matrix[j][i]`
- Diagonal: `matrix[i][i] = 1`

**Validation Rules**:
1. Matrix must be square (n × n)
2. Reciprocal property: A[i][j] × A[j][i] ≈ 1.0 (within tolerance)
3. Diagonal elements must be 1.0
4. CR < 0.1 for validation to pass
5. All elements > 0

**State Transitions**:
```
[Created] → pending → [Calculate CR] → valid (if CR < 0.1)
                                    → invalid (if CR ≥ 0.1)
```

**Example (YAML)**:
```yaml
matrix_id: "primary_capabilities"
expert_id: "expert_001"
comparison_scope: "C1-C5 primary capabilities"
dimension: 5

# Comparison matrix (5×5 for primary capabilities)
# Rows/Columns: C1, C2, C3, C4, C5
matrix:
  - [1.0, 2.0, 1.0, 3.0, 2.0]  # C1 vs all
  - [0.5, 1.0, 0.5, 2.0, 1.0]  # C2 vs all
  - [1.0, 2.0, 1.0, 3.0, 2.0]  # C3 vs all
  - [0.33, 0.5, 0.33, 1.0, 0.5]  # C4 vs all
  - [0.5, 1.0, 0.5, 2.0, 1.0]  # C5 vs all

# Computed values (filled by ahp_module.py)
calculated_cr: 0.023  # < 0.1, valid
weights: [0.30, 0.15, 0.30, 0.10, 0.15]  # Normalized principal eigenvector
validation_status: "valid"
```

**File Location**: `data/expert_judgments/*.yaml`

---

## Entity 4: Fuzzy Evaluation Set

**Purpose**: Defines linguistic terms and membership functions for qualitative indicators

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `evaluation_set_id` | string | required, unique | Identifier (e.g., "combat_quality_4level") |
| `linguistic_terms` | dict | required | Map of term names to quantified values |
| `applicable_indicators` | array[string] | required | Indicator IDs that use this fuzzy set |
| `expert_consensus` | dict | optional | Distribution of expert assessments |

**Linguistic Terms Sub-structure**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `term_name` | string | required, unique within set | Chinese linguistic label (e.g., "差", "中", "良", "优") |
| `quantified_value` | float | 0.0 ≤ value ≤ 1.0 | Crisp score for defuzzification |

**Expert Consensus Sub-structure** (per indicator):

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `indicator_id` | string | required | Which indicator this assessment applies to |
| `assessments` | dict | required | Count of experts selecting each linguistic term |
| `membership_vector` | array[float] | computed, sum = 1.0 | Normalized distribution (membership degrees) |
| `fuzzy_score` | float | computed, 0.0 ≤ score ≤ 1.0 | Weighted average for this indicator |

**Validation Rules**:
1. Quantified values must be in [0, 1] and strictly increasing (差 < 中 < 良 < 优)
2. Membership vector must sum to 1.0 (±0.001 tolerance)
3. At least 3 experts should provide assessments (for statistical validity)
4. Fuzzy score must be in [0, 1]

**Example (YAML)**:
```yaml
evaluation_set_id: "combat_quality_4level"

linguistic_terms:
  差:
    quantified_value: 0.25
  中:
    quantified_value: 0.50
  良:
    quantified_value: 0.75
  优:
    quantified_value: 1.00

applicable_indicators: ["P1_3", "P2_2", "P3_3", "P4_3", "P5_3"]  # 40% qualitative

expert_consensus:
  P1_3:  # 态势理解准确性
    indicator_id: "P1_3"
    assessments:
      差: 0
      中: 1
      良: 3
      优: 1
    membership_vector: [0.0, 0.2, 0.6, 0.2]  # Normalized counts
    fuzzy_score: 0.70  # 0.0×0.25 + 0.2×0.50 + 0.6×0.75 + 0.2×1.00 = 0.70
```

**File Location**: `config/fuzzy_sets.yaml`

---

## Entity 5: Evaluation Result

**Purpose**: Stores output from the AHP-FCE-TOPSIS evaluation pipeline

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `result_id` | string | required, unique | UUID or timestamp-based ID |
| `configuration_id` | string | required, foreign key | Reference to evaluated configuration |
| `scenario_id` | string | required | Scenario context (e.g., "strait_control") |
| `raw_indicator_values` | array[float] | required, length = 15 | Raw values for all 15 indicators |
| `normalized_values` | array[float] | computed, length = 15 | After vector normalization |
| `weighted_values` | array[float] | computed, length = 15 | After applying AHP weights |
| `topsis_metrics` | dict | computed | TOPSIS distance metrics |
| `final_ci_score` | float | required, 0.0 ≤ Ci ≤ 1.0 | Relative closeness to ideal solution |
| `rank` | integer | optional, ≥ 1 | Ranking among compared configurations |
| `timestamp` | datetime | required | When evaluation was performed |
| `audit_log_path` | string | optional | Path to detailed transformation log |

**TOPSIS Metrics Sub-structure**:

| Field | Type | Description |
|-------|------|-------------|
| `D_plus` | float | Euclidean distance to positive ideal solution (PIS) |
| `D_minus` | float | Euclidean distance to negative ideal solution (NIS) |
| `PIS` | array[float] | Positive ideal solution vector (length = 15) |
| `NIS` | array[float] | Negative ideal solution vector (length = 15) |

**Validation Rules**:
1. `raw_indicator_values` must contain exactly 15 values (one per indicator)
2. All intermediate arrays (normalized, weighted) must be same length
3. `final_ci_score` must be in [0, 1]
4. `D_plus + D_minus > 0` (denominator check for Ci calculation)

**State Transitions**: Immutable once created (read-only after evaluation completes)

**Example (JSON)**:
```json
{
  "result_id": "eval_2025102512345",
  "configuration_id": "baseline",
  "scenario_id": "strait_control",
  "raw_indicator_values": [
    0.75, 2.5, 0.70,
    3.2, 0.85, 4.1,
    0.82, 0.88, 0.75,
    0.95, 150, 0.80,
    0.70, 2.5, 0.75
  ],
  "normalized_values": [0.55, 0.42, 0.48, ...],  # After normalization
  "weighted_values": [0.14, 0.08, 0.09, ...],  # After weighting
  "topsis_metrics": {
    "D_plus": 0.23,
    "D_minus": 0.67,
    "PIS": [1.0, 0.0, 1.0, ...],  # Best values per indicator
    "NIS": [0.0, 1.0, 0.0, ...]   # Worst values per indicator
  },
  "final_ci_score": 0.744,  # D_minus / (D_plus + D_minus)
  "rank": 2,
  "timestamp": "2025-10-25T14:23:45Z",
  "audit_log_path": "outputs/results/audit_eval_2025102512345.log"
}
```

**File Location**: `outputs/results/*.json`

---

## Entity 6: Optimization Run

**Purpose**: Captures complete genetic algorithm execution session and results

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `run_id` | string | required, unique | UUID or timestamp-based ID |
| `scenario_id` | string | required | Scenario context |
| `algorithm_params` | dict | required | GA configuration |
| `constraints` | dict | required | Operational constraints |
| `generation_history` | array[dict] | computed | Per-generation metrics |
| `final_best_solution` | dict | computed | Optimal configuration found |
| `termination_reason` | enum | required, values: `convergence`, `max_iterations`, `user_stop` | Why optimization ended |
| `execution_metadata` | dict | required | Performance metrics |

**Algorithm Params Sub-structure**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `population_size` | integer | ≥ 10 | Number of solutions per generation |
| `num_generations` | integer | ≥ 1 | Maximum generations to run |
| `parent_selection` | enum | values: `tournament`, `roulette`, `rank` | Selection method |
| `crossover_type` | enum | values: `single_point`, `two_point`, `uniform` | Crossover operator |
| `mutation_type` | enum | values: `random`, `swap`, `gaussian` | Mutation operator |
| `mutation_rate` | float | 0.0 ≤ rate ≤ 1.0 | Probability of gene mutation |

**Generation History Sub-structure** (per generation):

| Field | Type | Description |
|-------|------|-------------|
| `generation_num` | integer | Generation index (0-based) |
| `best_fitness` | float | Highest Ci score in this generation |
| `avg_fitness` | float | Average Ci score across population |
| `diversity` | float | Population diversity metric (0-1) |

**Final Best Solution Sub-structure**:

| Field | Type | Description |
|-------|------|-------------|
| `chromosome` | array[mixed] | Gene values (platform counts, coordinates, assignments) |
| `decoded_config` | dict | Human-readable configuration parameters |
| `predicted_ci` | float | Fitness score (Ci value) |

**Validation Rules**:
1. `population_size` and `num_generations` must be positive
2. Mutation rate must be in [0, 1]
3. All genes in chromosome must satisfy constraint bounds
4. `generation_history` length should equal `num_generations` (unless early termination)
5. Diversity metric must be in [0, 1]

**State Transitions**:
```
[Initialized] → running → [Generations complete] → terminated
                                                → user_stopped
```

**Example (JSON)**:
```json
{
  "run_id": "ga_2025102515678",
  "scenario_id": "strait_control",
  "algorithm_params": {
    "population_size": 20,
    "num_generations": 50,
    "parent_selection": "tournament",
    "crossover_type": "single_point",
    "mutation_type": "gaussian",
    "mutation_rate": 0.2
  },
  "constraints": {
    "max_budget": 50000000,
    "max_platforms": 20,
    "min_coverage": 100
  },
  "generation_history": [
    {"generation_num": 0, "best_fitness": 0.62, "avg_fitness": 0.48, "diversity": 0.85},
    {"generation_num": 1, "best_fitness": 0.65, "avg_fitness": 0.51, "diversity": 0.78},
    ...
    {"generation_num": 49, "best_fitness": 0.82, "avg_fitness": 0.74, "diversity": 0.42}
  ],
  "final_best_solution": {
    "chromosome": [5, 8, 120.3, 24.5, 2],
    "decoded_config": {
      "usv_type_a": 5,
      "uuv_type_b": 8,
      "deploy_x": 120.3,
      "deploy_y": 24.5,
      "patrol_mode": 2
    },
    "predicted_ci": 0.82
  },
  "termination_reason": "max_iterations",
  "execution_metadata": {
    "start_time": "2025-10-25T15:00:00Z",
    "end_time": "2025-10-25T15:04:32Z",
    "total_runtime_seconds": 272,
    "total_evaluations": 1000
  }
}
```

**File Location**: `outputs/results/ga_*.json`

---

## Data Model Summary

| Entity | Primary ID | File Format | Location | Mutable? |
|--------|-----------|-------------|----------|----------|
| Indicator Hierarchy | `objective` | YAML | `config/indicators.yaml` | No |
| Combat System Configuration | `id` | YAML | `data/schemes/*.yaml` | No |
| Expert Judgment Matrix | `matrix_id` | YAML | `data/expert_judgments/*.yaml` | No (after validation) |
| Fuzzy Evaluation Set | `evaluation_set_id` | YAML | `config/fuzzy_sets.yaml` | No |
| Evaluation Result | `result_id` | JSON | `outputs/results/*.json` | No |
| Optimization Run | `run_id` | JSON | `outputs/results/ga_*.json` | No |

**Relationships**:
- `Evaluation Result` → `Combat System Configuration` (many-to-one)
- `Evaluation Result` → `Indicator Hierarchy` (uses for structure)
- `Evaluation Result` → `Fuzzy Evaluation Set` (uses for qualitative indicators)
- `Optimization Run` → `Evaluation Result` (generates many)
- `Expert Judgment Matrix` → `Indicator Hierarchy` (determines weights for)

**Phase 1 Completion**: ✅ Data model fully specified, ready for contract generation
