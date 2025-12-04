# AHP-FCE-TOPSIS Combat System Evaluation Constitution

<!--
  Sync Impact Report - Constitution Update

  Version Change: INITIAL → 1.0.0

  Modified Principles:
  - NEW: I. Modular Architecture
  - NEW: II. Data-Driven Evaluation
  - NEW: III. Scientific Rigor
  - NEW: IV. Rapid Prototyping
  - NEW: V. Documentation & Reproducibility

  Added Sections:
  - Core Principles (5 principles)
  - Technical Standards
  - Research Quality Requirements
  - Governance

  Removed Sections:
  - None (initial version)

  Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - reviewed, compatible
  ✅ .specify/templates/spec-template.md - reviewed, compatible
  ✅ .specify/templates/tasks-template.md - reviewed, compatible
  ⚠ .specify/templates/commands/*.md - no command files exist yet

  Follow-up TODOs:
  - None - all placeholders filled with concrete values
-->

## Core Principles

### I. Modular Architecture

**MUST** maintain strict separation between evaluation and optimization components:
- AHP, FCE, and TOPSIS modules MUST be independently callable and testable
- Genetic Algorithm (GA) optimizer MUST depend only on the evaluation interface, not implementation details
- Simulation logic MUST be decoupled from evaluation logic through clear interfaces
- Each module MUST have a single, well-defined responsibility

**Rationale**: The AHP-FCE-TOPSIS evaluation pipeline and GA optimization are conceptually distinct. Modular design enables independent validation, testing of evaluation logic without running optimization, and easy replacement of simplified simulation with complex models in future iterations.

### II. Data-Driven Evaluation

**MUST** ensure all evaluation decisions are traceable to source data:
- Expert judgment matrices (AHP) MUST be stored in version-controlled configuration files
- Fuzzy evaluation sets (FCE) MUST be explicitly defined and documented
- Indicator values from simulation MUST be logged with full provenance
- TOPSIS normalization and weighting MUST preserve audit trail from raw values to final Ci scores

**Rationale**: Military effectiveness evaluation requires justifiable, reproducible results. Data-driven approach enables peer review, sensitivity analysis, and compliance with research rigor standards outlined in referenced literature (Saaty 2008, Hatami-Marbini 2017).

### III. Scientific Rigor (NON-NEGOTIABLE)

**MUST** implement all theoretical requirements from established methods:
- AHP: Consistency ratio (CR) MUST be calculated and validated < 0.1 for all judgment matrices
- FCE: Membership degree normalization MUST sum to 1.0 for all fuzzy evaluations
- TOPSIS: Positive and negative ideal solutions MUST be correctly identified based on indicator types (benefit/cost)
- GA: Chromosome encoding MUST preserve feasibility constraints (e.g., platform counts ≥ 0, total cost ≤ budget)

**Test Gate**: Implementation MUST include validation functions that verify mathematical properties. All validation tests MUST pass before results are considered valid.

**Rationale**: Incorrect application of these methods produces meaningless results. The referenced literature (Zadeh 1965, Boyd 1987) establishes non-negotiable mathematical foundations that MUST be preserved.

### IV. Rapid Prototyping

**MUST** prioritize working implementation over perfect simulation:
- Simplified mathematical models are ACCEPTABLE for initial validation (avoid premature Mesa/complex simulation)
- Hardcoded test data is ACCEPTABLE during development (expert matrices, fuzzy sets)
- 3-5 test scenarios is SUFFICIENT for proof-of-concept
- Visualization quality is SECONDARY to computational correctness

**Trade-off Policy**: When choosing between simulation realism and iteration speed, choose speed for prototype phase. Document assumptions and simplifications for future enhancement.

**Rationale**: Project requires rapid validation of the integrated AHP-FCE-TOPSIS-GA pipeline. Complex agent-based simulation (Mesa) can be added after proving core methodology works.

### V. Documentation & Reproducibility

**MUST** maintain research-grade documentation:
- All indicator definitions MUST reference theoretical source (C1-C5 mapped to Alberts 2000, Boyd 1987, etc.)
- Configuration files MUST include inline citations for parameter choices
- Optimization results MUST be accompanied by execution parameters (GA population size, generations, mutation rate)
- Code MUST include docstrings linking implementation to methodology sections in research documents

**Output Requirements**:
- Evaluation module MUST generate audit logs showing: raw indicator values → normalized values → weighted values → Ci scores
- GA optimizer MUST export: convergence curve, best solution parameters, diversity metrics

**Rationale**: Research deliverables require full reproducibility. This project feeds into academic reporting (研究总报告, 咨询报告) requiring citation-backed methodology.

## Technical Standards

### Language & Dependencies

- **Language**: Python 3.8+ (for compatibility with PyGAD, NumPy ecosystem)
- **Core Libraries**:
  - `numpy` ≥1.21 (matrix operations, eigenvalue computation for AHP)
  - `pandas` ≥1.3 (data structures, indicator tables)
  - `pygad` ≥3.0 (genetic algorithm implementation)
  - `matplotlib` ≥3.5 (results visualization)
- **Optional**: `scipy` (if advanced statistical validation needed)

### Project Structure

**MUST** follow this layout (see implementation plan):

```
ahp_fce_topsis/
├── config/             # Declarative configuration
├── modules/            # Core algorithms (ahp, fce, topsis, ga, evaluator)
├── data/               # Expert judgments, scheme parameters
├── utils/              # Validation, normalization, visualization
└── outputs/            # Generated reports and plots
```

### Performance Constraints

- AHP weight calculation MUST complete in < 1 second for 5×5 matrices
- Full evaluation pipeline (AHP+FCE+TOPSIS) MUST process single scheme in < 0.5 seconds
- GA optimization (50 generations, 20 population) MUST complete in < 5 minutes for simplified simulation
- Memory footprint MUST remain < 500MB for target problem scale

**Rationale**: Prototype should run on standard laptop. GA requires thousands of fitness evaluations, so per-evaluation cost directly impacts feasibility.

## Research Quality Requirements

### Indicator System Validation

**MUST** validate 15 secondary indicators (3 per primary capability C1-C5):
- Each indicator MUST be mapped to at least one literature reference
- Mix of quantitative (60%) and qualitative (40%) indicators is REQUIRED
- Benefit vs. cost type MUST be explicitly declared for each indicator
- Indicator definitions MUST align with 五个一级评估维度 from specification documents

### Method Integration Checkpoints

1. **AHP Checkpoint**:
   - All judgment matrices pass CR < 0.1
   - Combined weights sum to 1.0
   - Sensitivity analysis shows stable rankings under ±20% weight perturbation

2. **FCE Checkpoint**:
   - All fuzzy membership degrees ∈ [0,1] and sum to 1.0
   - Linguistic evaluations (差/中/良/优) consistently mapped across experts
   - Quantified scores ∈ [0,1] and monotonically increase with quality

3. **TOPSIS Checkpoint**:
   - Normalization preserves indicator ranking order
   - Ideal solutions (PIS/NIS) correctly identified for all benefit/cost types
   - Relative closeness Ci ∈ [0,1] with clear separation between schemes

4. **GA Checkpoint**:
   - Fitness function monotonically improves over generations (convergence)
   - Best solution satisfies all constraints (feasibility)
   - Population diversity maintained above 0.3 (avoid premature convergence)

### Deliverable Standards

**Research Report** MUST include:
- Complete methodology section citing all 6 references from indicator system document
- Full indicator hierarchy table with weights
- Comparison table showing Ci scores for all evaluated schemes
- Convergence analysis for GA optimization

**Code Deliverable** MUST include:
- Runnable example with sample data
- Unit tests for CR calculation, normalization functions, fitness evaluation
- Configuration templates for new scenarios

## Governance

### Amendment Process

1. **Proposal**: Document proposed change with rationale and impact assessment
2. **Validation**: Verify change maintains scientific rigor and literature alignment
3. **Review**: Check for conflicts with research methodology documents
4. **Migration**: Update affected templates, code, and documentation
5. **Version Bump**: Follow semantic versioning (see below)

### Versioning Policy

- **MAJOR** (X.0.0): Breaking changes to indicator system, evaluation pipeline architecture, or method selection
- **MINOR** (x.Y.0): Adding new indicators, new visualization features, performance optimizations
- **PATCH** (x.y.Z): Bug fixes, documentation clarifications, parameter tuning

### Compliance Review

**Pre-Implementation**: Before writing code, verify plan against:
- Modular Architecture (Principle I) - components properly separated?
- Scientific Rigor (Principle III) - all mathematical requirements included?
- Documentation (Principle V) - traceability to research documents ensured?

**During Implementation**: Code reviews MUST check:
- All indicators have defined source references
- Validation functions exist and pass
- Configuration is externalized (no hardcoded weights in algorithm code)

**Pre-Delivery**: Final validation MUST confirm:
- All checkpoints passed (AHP, FCE, TOPSIS, GA)
- Deliverable standards met (reports, runnable code)
- Results align with expected theoretical behavior

### Complexity Justification

If implementation plan proposes complexity beyond this constitution (e.g., adding Mesa simulation before prototype validation, using custom GA implementation instead of PyGAD), justification MUST address:

1. **Why simpler alternative insufficient**: Specific limitation of standard approach
2. **Benefit quantification**: Measurable improvement (accuracy, performance, capability)
3. **Risk mitigation**: How added complexity affects timeline and maintenance

**Default stance**: Reject unjustified complexity in prototype phase per Principle IV.

---

**Version**: 1.0.0 | **Ratified**: 2025-10-25 | **Last Amended**: 2025-10-25
