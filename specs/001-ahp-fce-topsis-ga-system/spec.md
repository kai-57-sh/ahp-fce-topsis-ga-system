# Feature Specification: AHP-FCE-TOPSIS-GA Evaluation System

**Feature Branch**: `001-ahp-fce-topsis-ga-system`
**Created**: 2025-10-25
**Status**: Draft
**Input**: User description: "Implement AHP-FCE-TOPSIS hybrid evaluation model integrated with genetic algorithm optimization for unmanned combat system effectiveness assessment"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Combat System Evaluation (Priority: P1)

As a military systems analyst, I need to evaluate the effectiveness of different unmanned combat system configurations across multiple performance dimensions (situational awareness, command capability, strike capability, network connectivity, survivability) so that I can identify which configuration best meets operational requirements.

**Why this priority**: This is the core capability that enables any effectiveness comparison. Without it, analysts cannot objectively assess system performance or justify resource allocation decisions.

**Independent Test**: Can be fully tested by providing 3-5 predefined combat system configurations with known indicator values and verifying that the system produces consistent, mathematically valid effectiveness scores (Ci values) ranked from best to worst.

**Acceptance Scenarios**:

1. **Given** 3 combat system configurations with different platform mixes (USV/UUV counts), **When** the analyst inputs indicator data for all 15 secondary indicators across 5 capability dimensions, **Then** the system calculates weighted effectiveness scores and ranks configurations from highest to lowest effectiveness
2. **Given** indicator data for a single combat system, **When** the analyst requests evaluation, **Then** the system generates a comprehensive report showing: raw indicator values, normalized values, weighted scores, and final Ci score between 0 and 1
3. **Given** inconsistent expert judgment inputs (AHP matrices with CR ≥ 0.1), **When** the analyst attempts evaluation, **Then** the system rejects the evaluation and identifies which judgment matrices fail consistency requirements
4. **Given** fuzzy qualitative assessments from multiple experts (差/中/良/优), **When** the analyst processes these through FCE, **Then** the system converts all qualitative indicators to quantified scores between 0 and 1 with full audit trail

---

### User Story 2 - System Configuration Optimization (Priority: P2)

As a mission planner, I need to automatically discover optimal combat system configurations that maximize effectiveness within budget and operational constraints (platform limits, deployment zones, mission assignments) so that I can deploy the most capable force structure without exhaustively testing every possible combination.

**Why this priority**: Manual exploration of the configuration space is infeasible (thousands of combinations). This story delivers the AI-powered optimization that finds near-optimal solutions efficiently.

**Independent Test**: Can be fully tested by defining a constrained optimization problem (e.g., "maximize effectiveness with ≤10 platforms, total cost ≤$50M, coverage area ≥100km²"), running the genetic algorithm for a fixed number of generations, and verifying that the best solution satisfies all constraints and shows monotonic improvement over generations.

**Acceptance Scenarios**:

1. **Given** optimization parameters (platform types available, cost constraints, operational requirements), **When** the planner runs genetic algorithm optimization for 50 generations with population size 20, **Then** the system produces a recommended configuration with higher effectiveness score than any manually-specified baseline
2. **Given** a running optimization process, **When** the planner monitors progress, **Then** the system displays real-time convergence curves showing best fitness, average fitness, and population diversity at each generation
3. **Given** an optimized solution, **When** the planner examines results, **Then** the system provides full specification of the recommended configuration including: platform counts by type, deployment coordinates, task assignments, and predicted effectiveness score
4. **Given** competing operational priorities (maximize coverage vs minimize cost), **When** the planner runs multiple optimization scenarios with different constraint weights, **Then** the system produces distinct recommendations reflecting the tradeoff space

---

### User Story 3 - Sensitivity Analysis & Validation (Priority: P3)

As a research analyst, I need to validate the robustness of evaluation results by performing sensitivity analysis on indicator weights and expert judgments so that I can ensure recommendations remain stable under reasonable variations in assessment parameters and satisfy scientific rigor standards for publication.

**Why this priority**: While not required for basic operation, this story ensures the system meets academic research standards and builds confidence in results through transparent validation.

**Independent Test**: Can be fully tested by perturbing indicator weights by ±20% and verifying that configuration rankings remain stable (same top-3 systems), and by regenerating fuzzy membership functions with different expert consensus levels to confirm score variations stay within acceptable bounds (±10%).

**Acceptance Scenarios**:

1. **Given** a completed evaluation with baseline indicator weights, **When** the analyst perturbs each weight by ±20% independently, **Then** the system recalculates all scores and reports whether configuration rankings changed significantly
2. **Given** fuzzy evaluation data from 5 experts, **When** the analyst removes one expert's opinions at a time (jackknife method), **Then** the system shows whether the final Ci scores remain within ±10% of the full consensus value
3. **Given** evaluation results, **When** the analyst requests a validation report, **Then** the system generates documentation showing: AHP consistency ratios for all matrices, FCE membership degree distributions, TOPSIS ideal solution verification, and GA convergence metrics
4. **Given** multiple evaluation scenarios (different combat contexts), **When** the analyst compares results, **Then** the system highlights indicators that show high variance across scenarios versus those that remain stable

---

### Edge Cases

- What happens when all expert judgments are identical (perfect consensus)? System should still calculate valid weights without numerical instability.
- What happens when two configurations produce identical Ci scores? System should report them as tied and flag for manual review.
- What happens when GA optimization cannot find any feasible solution within constraint bounds? System should report infeasibility and suggest constraint relaxation.
- What happens when an indicator has zero variance across all configurations (e.g., all systems have same communication range)? System should handle normalization gracefully without division by zero.
- What happens when indicator data contains outliers or measurement errors? System should flag extreme values for review before processing.
- What happens when optimization is interrupted mid-execution? System should allow resumption from last completed generation or gracefully return best solution found so far.

## Requirements *(mandatory)*

### Functional Requirements

#### Evaluation Pipeline (User Story 1)

- **FR-001**: System MUST implement Analytic Hierarchy Process (AHP) to calculate indicator weights from expert pairwise comparison matrices for all 5 primary capabilities and 15 secondary indicators
- **FR-002**: System MUST validate all AHP judgment matrices against consistency ratio (CR) threshold of 0.1 and reject evaluations that exceed this threshold
- **FR-003**: System MUST implement Fuzzy Comprehensive Evaluation (FCE) to convert qualitative expert assessments (差/中/良/优) into quantified scores between 0 and 1
- **FR-004**: System MUST ensure all FCE fuzzy membership degrees sum to 1.0 for each qualitative indicator
- **FR-005**: System MUST implement TOPSIS method to rank combat system configurations by calculating relative closeness (Ci) to ideal solutions
- **FR-006**: System MUST correctly identify positive ideal solution (PIS) and negative ideal solution (NIS) based on whether each indicator is benefit-type or cost-type
- **FR-007**: System MUST normalize indicator values using vector normalization to eliminate scale differences while preserving ranking order
- **FR-008**: System MUST generate evaluation audit logs showing the complete transformation chain: raw values → normalized values → weighted values → Ci scores
- **FR-009**: System MUST evaluate configurations against 15 secondary indicators organized under 5 primary capabilities: C1-Situational Awareness (3 indicators), C2-Command Capability (3 indicators), C3-Strike Capability (3 indicators), C4-Network Connectivity (3 indicators), C5-Survivability (3 indicators)

#### Optimization Engine (User Story 2)

- **FR-010**: System MUST implement genetic algorithm optimizer with configurable parameters: population size, number of generations, crossover rate, mutation rate, selection method
- **FR-011**: System MUST encode combat system configurations as chromosomes representing: platform counts by type (integer), deployment coordinates (float), task assignments (permutation)
- **FR-012**: System MUST use the AHP-FCE-TOPSIS evaluation pipeline as the fitness function for genetic algorithm optimization
- **FR-013**: System MUST enforce operational constraints during chromosome generation and mutation: minimum/maximum platform counts, budget limits, deployment zone boundaries, task coverage requirements
- **FR-014**: System MUST track and report optimization progress metrics: best fitness per generation, average fitness per generation, population diversity per generation
- **FR-015**: System MUST support multiple genetic operators: tournament selection, roulette wheel selection, single-point crossover, uniform crossover, Gaussian mutation for continuous variables, swap mutation for discrete variables
- **FR-016**: System MUST output complete specification of optimized configuration including all decision variables and predicted effectiveness score

#### Validation & Analysis (User Story 3)

- **FR-017**: System MUST perform sensitivity analysis by perturbing indicator weights within user-specified ranges (default ±20%) and reporting impact on configuration rankings
- **FR-018**: System MUST support jackknife validation for fuzzy evaluations by systematically excluding each expert and measuring score stability
- **FR-019**: System MUST generate validation reports documenting: all AHP CR values, FCE membership distributions, TOPSIS ideal solution calculations, GA convergence behavior
- **FR-020**: System MUST flag potential data quality issues: zero-variance indicators, extreme outlier values, non-converging optimization runs

#### Data Management

- **FR-021**: System MUST store expert judgment matrices in structured configuration files with version control support
- **FR-022**: System MUST store fuzzy evaluation sets (linguistic terms and membership functions) in declarative configuration separate from algorithm code
- **FR-023**: System MUST persist evaluation results including: input data snapshot, calculated weights, intermediate computations, final scores, timestamps
- **FR-024**: System MUST export results in formats suitable for research reporting: tabular data for indicator hierarchies, comparison tables for configuration rankings, visualization data for charts

#### User Interface & Reporting

- **FR-025**: System MUST provide clear error messages when validation fails (e.g., "AHP matrix for C2-Command Capability has CR=0.15, exceeding threshold of 0.1")
- **FR-026**: System MUST generate visualizations: bar charts comparing Ci scores across configurations, convergence curves for GA optimization, radar charts showing multi-dimensional capability profiles
- **FR-027**: System MUST allow users to define new combat scenarios via YAML configuration files by specifying: scenario name, operational context, indicator target values, constraint parameters (platform limits, budget, deployment bounds)
- **FR-028**: System MUST support batch evaluation of multiple configurations with summary comparison reports

### Key Entities

- **Indicator Hierarchy**: Represents the 5-level structure (Objective → Primary Capabilities → Secondary Indicators) with weights at each level. Each indicator has: unique ID, name, description, measurement unit, benefit/cost type, weight value, literature reference source.

- **Combat System Configuration**: Represents a specific force structure design with: configuration ID, platform inventory (counts by USV/UUV type), deployment plan (geographic coordinates), task assignment matrix (platform-to-mission mapping), operational constraints, metadata (author, creation date, scenario context).

- **Expert Judgment Matrix**: Represents pairwise comparison data from AHP process with: matrix ID, expert ID, comparison scope (which indicators being compared), pairwise values (typically 1-9 scale), calculated consistency ratio, weight vector result, validation status.

- **Fuzzy Evaluation Set**: Represents qualitative assessment mapping with: evaluation set ID, linguistic terms (差/中/良/优), membership functions, quantified score values (0.25/0.50/0.75/1.0), applicable indicators, expert consensus distribution.

- **Evaluation Result**: Represents output from assessment pipeline with: result ID, configuration reference, scenario reference, raw indicator values (15 values), normalized values, weighted values, TOPSIS distance metrics (D+, D-), final Ci score, rank among compared configurations, generation timestamp, audit log reference.

- **Optimization Run**: Represents a GA execution session with: run ID, scenario reference, algorithm parameters (population size, generations, operators), constraint specifications, generation-by-generation history (best/avg/diversity), final best solution (chromosome representation), termination reason (convergence/iteration limit), execution metadata (start/end time, computational cost).

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Evaluation Accuracy & Validity

- **SC-001**: All AHP consistency ratios must remain below 0.1 threshold, demonstrating mathematically sound expert judgments
- **SC-002**: FCE fuzzy membership degrees must sum to 1.0 (±0.001 tolerance) for all qualitative indicators, ensuring proper probability normalization
- **SC-003**: TOPSIS Ci scores must fall within [0, 1] range with clear separation between consecutively ranked configurations (minimum 0.05 difference between rank N and rank N+1) to enable meaningful distinction
- **SC-004**: Evaluation of a single configuration (all 15 indicators) must complete in under 0.5 seconds on standard hardware

#### Optimization Performance

- **SC-005**: Genetic algorithm optimization must demonstrate monotonic improvement, with best fitness increasing by at least 10% over baseline within 50 generations
- **SC-006**: Optimization run (50 generations, population 20) must complete in under 5 minutes for simplified simulation models
- **SC-007**: Final optimized configuration must satisfy 100% of specified hard constraints (budget, platform limits, coverage requirements)
- **SC-008**: Population diversity metric must remain above 0.3 throughout optimization to avoid premature convergence

#### Validation & Robustness

- **SC-009**: Sensitivity analysis with ±20% weight perturbation must preserve top-3 configuration rankings in at least 80% of test scenarios
- **SC-010**: Jackknife validation (removing one expert) must keep Ci score variations within ±10% of consensus value
- **SC-011**: System must correctly handle edge cases (identical scores, zero variance, infeasibility) without crashes or numerical errors

#### Research Quality & Reproducibility

- **SC-012**: Every evaluation result must include complete audit trail from raw data to final scores, enabling independent verification
- **SC-013**: Validation reports must document all required mathematical properties: AHP CR values, FCE normalization, TOPSIS ideal solutions, GA convergence
- **SC-014**: System must support comparison of at least 5 configurations simultaneously with results exportable for academic publication

#### Usability & Workflow

- **SC-015**: Analysts must be able to complete a full evaluation workflow (data input → weight calculation → evaluation → reporting) for 3 configurations in under 10 minutes
- **SC-016**: Error messages for validation failures must clearly identify the problem source and suggest corrective actions (90% of users understand error without external help)
- **SC-017**: Generated visualizations (charts, plots, tables) must meet academic publication standards with proper labeling, legends, and references

### Assumptions

- Expert judgment matrices will be provided by domain experts familiar with AHP methodology and military system assessment
- Indicator data for combat systems can be obtained through simplified mathematical simulation models during prototype phase (detailed agent-based simulation deferred to future enhancement)
- Standard desktop/laptop hardware (8GB RAM, modern multi-core CPU) is sufficient for prototype deployment
- Results will be primarily consumed by technical analysts familiar with multi-criteria decision analysis concepts
- Fuzzy evaluation will use 4-level linguistic scale (差/中/良/优) based on established Chinese military assessment practices
- Initial deployment will focus on 3-5 test scenarios covering representative operational contexts (strait control, landing zone clearance, etc.)
- Genetic algorithm implementation will use established open-source library (PyGAD) rather than custom implementation
- All indicator definitions and weights will reference published military systems engineering literature (Alberts 2000, Boyd 1987, Chinese DoD research standards)
