# Tasks: AHP-FCE-TOPSIS-GA Evaluation System

**Input**: Design documents from `/specs/001-ahp-fce-topsis-ga-system/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. Focus on implementation and validation functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `modules/`, `utils/`, `config/`, `data/`, `tests/` at repository root
- Paths shown below follow single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: modules/, utils/, config/, data/, outputs/, tests/
- [ ] T002 Initialize Python project with requirements.txt (numpy>=1.21, pandas>=1.3, pygad>=3.0, matplotlib>=3.5, pyyaml>=6.0, pytest>=7.0)
- [ ] T003 [P] Create .gitignore for outputs/, __pycache__/, *.pyc, venv/
- [ ] T004 [P] Create README.md with project overview and setup instructions
- [ ] T005 [P] Create modules/__init__.py for package initialization
- [ ] T006 [P] Create utils/__init__.py for package initialization

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create config/indicators.yaml template with 5 primary capabilities (C1-C5) and 15 secondary indicators (P1_1-P5_3), including weight placeholders, type (benefit/cost), fuzzy flags, and literature references
- [ ] T008 Create config/fuzzy_sets.yaml defining 4-level linguistic scale (差:0.25, 中:0.50, 良:0.75, 优:1.00) with applicable indicators list
- [ ] T009 [P] Create data/expert_judgments/primary_capabilities.yaml template with 5×5 comparison matrix structure
- [ ] T010 [P] Create data/expert_judgments/secondary_indicators/ directory with templates for c1_indicators.yaml through c5_indicators.yaml (3×3 matrices each)
- [ ] T011 [P] Create data/schemes/ directory with baseline_scheme.yaml, scheme_a.yaml, scheme_b.yaml templates containing platform_inventory, deployment_plan, task_assignments structures
- [ ] T012 [P] Create config/scenarios/ directory with strait_control.yaml template including constraints (max_budget, max_platforms, deployment_bounds)
- [ ] T013 Implement utils/consistency_check.py with calculate_cr() function using eigenvalue method and Random Index (RI) lookup table for CR calculation
- [ ] T014 [P] Implement utils/normalization.py with vector_normalize() function for TOPSIS normalization
- [ ] T015 [P] Implement utils/validation.py with log_transformation() for audit trail logging and validate_evaluation_result() for schema validation
- [ ] T016 [P] Create outputs/ subdirectories: results/, reports/, plots/ (git-ignored)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Combat System Evaluation (Priority: P1) 🎯 MVP

**Goal**: Implement AHP-FCE-TOPSIS evaluation pipeline to rank combat system configurations

**Independent Test**: Evaluate 3 sample configurations (baseline, scheme_a, scheme_b) and verify: (1) all Ci scores in [0,1], (2) rankings are consistent, (3) AHP CR < 0.1 for all matrices, (4) audit logs show complete transformation chain

### Implementation for User Story 1

- [ ] T017 [P] [US1] Implement modules/ahp_module.py with calculate_weights(judgment_matrix) function using numpy.linalg.eig() for eigenvalue decomposition, returning weights, lambda_max, CR, and valid flag
- [ ] T018 [P] [US1] Implement validate_judgment_matrix() in modules/ahp_module.py to check square property, diagonal=1.0, reciprocal property A[i][j]*A[j][i]≈1.0
- [ ] T019 [P] [US1] Implement modules/fce_module.py with fuzzy_evaluate(expert_assessments, fuzzy_scale) function to convert linguistic terms to membership vectors and calculate fuzzy scores via weighted average
- [ ] T020 [P] [US1] Implement validate_membership_degrees() in modules/fce_module.py to ensure sum=1.0 within tolerance
- [ ] T021 [P] [US1] Implement modules/topsis_module.py with topsis_rank(decision_matrix, weights, indicator_types) function including vector normalization, ideal solution identification (PIS/NIS), distance calculation (D+, D-), and Ci score computation
- [ ] T022 [P] [US1] Implement identify_ideal_solutions(weighted_matrix, indicator_types) in modules/topsis_module.py to correctly set PIS=max/min and NIS=min/max based on benefit/cost types
- [ ] T023 [US1] Implement modules/evaluator.py with evaluate_single_scheme(scheme_data, indicator_config, fuzzy_config, expert_judgments) orchestrating full pipeline: extract indicators → apply FCE to qualitative → construct decision matrix → run TOPSIS → generate audit log
- [ ] T024 [US1] Implement evaluate_batch(schemes, indicator_config, fuzzy_config, expert_judgments) in modules/evaluator.py to evaluate multiple configurations and assign ranks based on Ci scores
- [ ] T025 [US1] Add validation in modules/evaluator.py to call utils/consistency_check.py for all AHP matrices and reject if any CR ≥ 0.1 with actionable error message
- [ ] T026 [US1] Implement audit logging in modules/evaluator.py calling utils/validation.py log_transformation() at each pipeline stage (raw→normalized→weighted→Ci)
- [ ] T027 [US1] Create main.py CLI with 'evaluate' command accepting --schemes (paths to YAML files), --batch flag, --output (JSON result path), loading configs from config/ and data/expert_judgments/
- [ ] T028 [US1] Add error handling to main.py evaluate command to catch AHPConsistencyError, ValidationError, and provide user-friendly messages per FR-025

**Checkpoint**: At this point, User Story 1 should be fully functional - analysts can evaluate and rank configurations

---

## Phase 4: User Story 2 - System Configuration Optimization (Priority: P2)

**Goal**: Implement genetic algorithm to discover optimal combat system configurations

**Independent Test**: Run GA optimization for strait_control scenario with max 10 platforms and verify: (1) best fitness improves by ≥10% from baseline, (2) final solution satisfies all constraints, (3) convergence curve shows monotonic improvement, (4) runtime <5 minutes

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement modules/ga_optimizer.py with decode_chromosome(chromosome, gene_config) function to convert gene array to CombatSystemConfiguration dict format
- [ ] T030 [P] [US2] Implement fitness_function(ga_instance, solution, solution_idx) in modules/ga_optimizer.py that: decodes chromosome → validates constraints → generates indicator values (simplified simulation) → calls evaluator.evaluate_single_scheme() → returns Ci score
- [ ] T031 [US2] Implement simplified simulation logic in modules/ga_optimizer.py to generate 15 indicator values from platform counts and deployment coordinates using mathematical formulas (documented in comments with references, placeholder for future Mesa integration)
- [ ] T032 [US2] Implement optimize_configuration(scenario_config, ga_params, constraints, evaluator_instance) in modules/ga_optimizer.py integrating PyGAD with custom fitness function, constraint validation during chromosome generation/mutation
- [ ] T033 [US2] Add generation history tracking in modules/ga_optimizer.py recording best_fitness, avg_fitness, and diversity metric for each generation
- [ ] T034 [US2] Implement constraint validation in modules/ga_optimizer.py to check platform counts ≥0, total platforms ≤ max_platforms, budget ≤ max_budget, coordinates within deployment_bounds
- [ ] T035 [US2] Add main.py CLI 'optimize' command accepting --scenario (YAML path), --population (int), --generations (int), --output (JSON result path)
- [ ] T036 [US2] Implement progress display in main.py optimize command showing [Generation X/Y] Best fitness, Avg fitness, Diversity for each generation
- [ ] T037 [US2] Implement main.py CLI 'extract-config' command to convert GA result JSON to YAML configuration file in data/schemes/
- [ ] T038 [US2] Create utils/visualization.py with plot_convergence(ga_results, output_path) function using matplotlib to generate convergence curve (best/avg fitness vs generation)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - planners can optimize configurations

---

## Phase 5: User Story 3 - Sensitivity Analysis & Validation (Priority: P3)

**Goal**: Implement validation tools for robustness testing and research publication

**Independent Test**: Run sensitivity analysis on comparison_001.json results with ±20% perturbation and verify: (1) rankings stable in ≥80% iterations, (2) top-3 preserved in 100% iterations, (3) Ci variation ≤±10%, (4) validation report includes all required metrics

### Implementation for User Story 3

- [ ] T039 [P] [US3] Implement sensitivity analysis module in utils/validation.py with perform_sensitivity_analysis(baseline_results, perturbation_pct, iterations) function
- [ ] T040 [US3] Implement weight perturbation logic in utils/validation.py to randomly vary each indicator weight by ±perturbation_pct, re-normalize to sum=1.0, re-run TOPSIS, compare rankings
- [ ] T041 [P] [US3] Implement jackknife validation in utils/validation.py with perform_jackknife_validation(fuzzy_data, evaluator) to systematically exclude each expert and measure Ci score stability
- [ ] T042 [US3] Implement validation report generator in utils/validation.py with generate_validation_report(evaluation_results) producing structured dict with AHP CR values, FCE distributions, TOPSIS PIS/NIS verification, GA convergence metrics
- [ ] T043 [US3] Add main.py CLI 'sensitivity' command accepting --baseline-results (JSON), --perturbation (float 0-1), --iterations (int), --output (JSON)
- [ ] T044 [US3] Implement ranking stability analysis in main.py sensitivity command to count how many iterations preserve baseline rankings and top-3 schemes
- [ ] T045 [US3] Add main.py CLI 'validate' command accepting --scheme (YAML path) or --ahp-matrix (YAML path) to validate individual configuration or judgment matrix
- [ ] T046 [US3] Extend utils/visualization.py with plot_sensitivity_results(sensitivity_json, output_path) to visualize ranking stability and Ci variation distributions

**Checkpoint**: All user stories should now be independently functional - researchers can validate robustness

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T047 [P] Extend utils/visualization.py with plot_comparison_chart(results_json, output_path) to generate bar chart comparing Ci scores across configurations
- [ ] T048 [P] Extend utils/visualization.py with plot_radar_chart(configuration_results, indicator_config, output_path) to show multi-dimensional capability profiles
- [ ] T049 [P] Add main.py CLI 'visualize' command supporting --plot-type (convergence|comparison|radar|sensitivity), routing to appropriate visualization function
- [ ] T050 [P] Implement main.py CLI 'report' command accepting --results (JSON), --include-methodology, --include-sensitivity, --format (pdf|md), generating comprehensive evaluation report with citations (PDF generation via matplotlib savefig or reportlab)
- [ ] T051 [P] Create tests/fixtures/ directory with sample_matrices.yaml (valid/invalid AHP matrices), sample_schemes.yaml (test configurations), sample_fuzzy_data.yaml
- [ ] T052 [P] Create tests/unit/test_ahp.py with test_calculate_weights_valid_matrix(), test_calculate_weights_invalid_cr(), test_validate_judgment_matrix_reciprocal_violation()
- [ ] T053 [P] Create tests/unit/test_fce.py with test_fuzzy_evaluate_membership_sum(), test_fuzzy_evaluate_score_range()
- [ ] T054 [P] Create tests/unit/test_topsis.py with test_topsis_rank_ci_range(), test_identify_ideal_solutions_benefit_cost()
- [ ] T055 [P] Create tests/integration/test_evaluation_pipeline.py with test_evaluate_single_scheme_end_to_end(), test_evaluate_batch_ranking_consistency()
- [ ] T056 [P] Create tests/integration/test_optimization_workflow.py with test_ga_optimization_constraint_satisfaction(), test_ga_optimization_convergence()
- [ ] T057 Add performance validation to tests/integration/test_evaluation_pipeline.py ensuring <0.5s per scheme evaluation (SC-004), <5min GA optimization (SC-006), and population diversity metric >0.3 throughout optimization run (SC-008)
- [ ] T058 [P] Populate config/indicators.yaml with actual weights from literature (Alberts 2000, Boyd 1987, etc.) and complete all 15 indicator definitions with references
- [ ] T059 [P] Populate data/expert_judgments/ with valid example matrices (CR < 0.1) for primary capabilities and all 5 secondary indicator groups
- [ ] T060 [P] Populate data/schemes/ with realistic baseline, scheme_a, scheme_b configurations including platform inventories and deployment plans
- [ ] T061 [P] Update README.md with complete setup instructions, usage examples for all 3 user stories, troubleshooting section, performance benchmarks
- [X] T062 Run full integration test suite (pytest tests/) and validate all success criteria SC-001 through SC-017

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - User Story 2 (Phase 4): Can start after Foundational - **Depends on US1** (uses evaluator as fitness function)
  - User Story 3 (Phase 5): Can start after Foundational - **Depends on US1** (validates evaluation results)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - **REQUIRES US1** for fitness function (modules/evaluator.py)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - **REQUIRES US1** for baseline evaluation results

**Critical Path**: Setup → Foundational → US1 → US2 → US3 → Polish

### Within Each User Story

**User Story 1 Flow**:
- T017-T022 (modules) can run in parallel (different files)
- T023-T024 (evaluator) depends on T017-T022 completion
- T025-T026 (validation/logging) depends on T023-T024
- T027-T028 (CLI) depends on T023-T026

**User Story 2 Flow**:
- T029-T034 (ga_optimizer) can mostly run in parallel, but T030 depends on T029, T032 depends on T029-T031
- T035-T038 (CLI/viz) depends on T029-T034

**User Story 3 Flow**:
- T039-T042 (validation utilities) can run in parallel (different functions in same file)
- T043-T046 (CLI) depends on T039-T042

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T006)
- All Foundational tasks marked [P] can run in parallel within each sub-group:
  - Config templates: T007-T008
  - Data templates: T009-T012
  - Utils implementation: T013-T015
- **User Story 1**: T017-T020 (AHP, FCE modules) can run fully in parallel
- **User Story 1**: T021-T022 (TOPSIS module) can run in parallel with T017-T020
- **User Story 2**: T029-T031 can run in parallel after understanding dependencies
- **User Story 3**: T039-T042 can run in parallel (independent validation functions)
- **Polish phase**: All tasks T047-T062 can run in parallel (different files/concerns)

---

## Parallel Example: User Story 1

```bash
# Launch all independent modules together:
Task: "Implement modules/ahp_module.py with calculate_weights()"
Task: "Implement modules/fce_module.py with fuzzy_evaluate()"
Task: "Implement modules/topsis_module.py with topsis_rank()"

# Then integrate in evaluator (sequential after modules done):
Task: "Implement modules/evaluator.py with evaluate_single_scheme()"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T016) - CRITICAL for all stories
3. Complete Phase 3: User Story 1 (T017-T028)
4. **STOP and VALIDATE**: Test with 3 sample configurations, verify Ci scores, check audit logs
5. Deploy/demo MVP - analysts can now evaluate configurations

**MVP Deliverable**: Combat system evaluation capability with AHP-FCE-TOPSIS pipeline

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T016)
2. Add User Story 1 → Test independently → Deploy/Demo (T017-T028) - **MVP!**
3. Add User Story 2 → Test independently → Deploy/Demo (T029-T038) - **Optimization!**
4. Add User Story 3 → Test independently → Deploy/Demo (T039-T046) - **Research validation!**
5. Polish & Testing → Full system (T047-T062)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T016)
2. Once Foundational is done:
   - Developer A: User Story 1 (T017-T028)
   - Developer A finishes US1, then:
     - Developer A: User Story 2 (T029-T038) - needs US1 complete
     - Developer B: User Story 3 (T039-T046) - needs US1 complete
3. Both complete Polish phase in parallel (T047-T062)

**Note**: US2 and US3 both require US1 complete, so cannot start before US1 is done.

---

## Task Summary

**Total Tasks**: 62

**By Phase**:
- Setup: 6 tasks
- Foundational: 10 tasks (BLOCKING)
- User Story 1 (P1): 12 tasks - **MVP**
- User Story 2 (P2): 10 tasks
- User Story 3 (P3): 8 tasks
- Polish: 16 tasks

**By User Story**:
- US1 (Combat System Evaluation): 12 tasks
- US2 (System Configuration Optimization): 10 tasks
- US3 (Sensitivity Analysis & Validation): 8 tasks
- Infrastructure (Setup + Foundational + Polish): 32 tasks

**Parallel Opportunities**: 35+ tasks can run in parallel (marked with [P])

**Independent Test Criteria**:
- US1: 3 configurations → Ci scores [0,1], CR < 0.1, audit logs complete
- US2: GA run → ≥10% improvement, constraints satisfied, <5min runtime
- US3: Sensitivity → ≥80% ranking stability, ±10% Ci variation

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (T001-T028) = 28 tasks for complete evaluation capability

**Estimated Timeline**:
- MVP (US1 only): 4 days
- MVP + US2 (with optimization): 5 days
- Full system (all 3 stories): 7 days
- With polish and testing: 7-8 days

---

## Notes

- All [US1], [US2], [US3] labels map tasks to specific user stories for traceability
- [P] tasks = different files, no dependencies within their phase
- Each user story is independently completable and testable per spec requirements
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are not included as separate tasks since not explicitly requested in spec - validation happens through mathematical property checks in implementation

---

## Format Validation ✅

All tasks follow required checklist format:
- ✅ Every task starts with `- [ ]` (checkbox)
- ✅ Every task has sequential ID (T001-T062)
- ✅ [P] marker only on parallelizable tasks
- ✅ [US1]/[US2]/[US3] labels on user story phase tasks
- ✅ Clear descriptions with file paths
- ✅ No story labels on Setup/Foundational/Polish phases
