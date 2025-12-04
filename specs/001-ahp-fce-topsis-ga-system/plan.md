# Implementation Plan: AHP-FCE-TOPSIS-GA Evaluation System

**Branch**: `001-ahp-fce-topsis-ga-system` | **Date**: 2025-10-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ahp-fce-topsis-ga-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This project implements a hybrid multi-criteria decision analysis system for evaluating unmanned combat system configurations. The system integrates three established methods (AHP for weight calculation, FCE for fuzzy evaluation, TOPSIS for ranking) into a unified evaluation pipeline, then uses genetic algorithm optimization to discover optimal system configurations. The technical approach prioritizes modular architecture with independent, testable components, scientific rigor through mathematical validation, and rapid prototyping using simplified simulation models.

## Technical Context

**Language/Version**: Python 3.8+ (minimum for NumPy/Pandas ecosystem compatibility)
**Primary Dependencies**:
  - `numpy` ≥1.21 (matrix operations, eigenvalue computation for AHP weights)
  - `pandas` ≥1.3 (data structures for indicator tables and results)
  - `pygad` ≥3.0 (genetic algorithm framework)
  - `matplotlib` ≥3.5 (visualization of results, convergence curves)
  - `pyyaml` or `json` (configuration file management)

**Storage**: File-based (JSON/YAML for configuration, CSV/JSON for results, no database required for prototype)

**Testing**: `pytest` ≥7.0 (unit tests for mathematical validations, integration tests for pipelines)

**Target Platform**: Cross-platform desktop (Linux/Windows/macOS), standard laptop hardware (8GB RAM, multi-core CPU)

**Project Type**: Single project (command-line tool with programmatic API, no web/mobile interface for prototype)

**Performance Goals**:
  - AHP weight calculation: <1 second for 5×5 judgment matrix
  - Full evaluation pipeline: <0.5 seconds per configuration (15 indicators)
  - GA optimization: <5 minutes for 50 generations with population of 20
  - Memory footprint: <500MB for typical workload

**Constraints**:
  - Mathematical correctness MUST NOT be compromised for performance
  - All calculations must be reproducible (deterministic except where randomness is explicit)
  - Results must be exportable for academic publication
  - Offline-capable (no external API dependencies)

**Scale/Scope**:
  - 5 primary capabilities, 15 secondary indicators (fixed hierarchy for prototype)
  - 3-5 test scenarios (representative combat contexts)
  - 3-10 configurations per evaluation batch
  - Support for 3-7 expert opinions in AHP matrices

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Modular Architecture (Principle I)
- [x] AHP, FCE, TOPSIS modules independently callable? **YES** - Each in separate `modules/*.py` file with standalone functions
- [x] GA optimizer depends only on evaluation interface? **YES** - `ga_optimizer.py` calls `evaluator.py` interface, not individual modules
- [x] Simulation decoupled from evaluation? **YES** - Simplified simulation in `data/schemes/`, evaluation in `modules/`
- [x] Single responsibility per module? **YES** - `ahp_module.py` (weights), `fce_module.py` (fuzzy), `topsis_module.py` (ranking), `ga_optimizer.py` (optimization), `evaluator.py` (orchestration)

### Data-Driven Evaluation (Principle II)
- [x] Expert judgments in version-controlled config files? **YES** - `data/expert_judgments/*.yaml` under version control
- [x] Fuzzy evaluation sets explicitly defined? **YES** - `config/fuzzy_sets.yaml` defines linguistic terms and membership functions
- [x] Indicator values logged with provenance? **YES** - `utils/validation.py` provides audit logging, results saved to `outputs/results/`
- [x] TOPSIS audit trail preserved? **YES** - Evaluation pipeline logs raw → normalized → weighted → Ci transformations

### Scientific Rigor (Principle III - NON-NEGOTIABLE)
- [x] AHP CR < 0.1 validation implemented? **YES** - `utils/consistency_check.py` calculates CR, rejects matrices with CR ≥ 0.1
- [x] FCE membership degrees sum to 1.0? **YES** - `fce_module.py` includes normalization validation
- [x] TOPSIS ideal solutions correctly identified? **YES** - `topsis_module.py` identifies PIS/NIS based on benefit/cost indicator types from config
- [x] GA chromosome encoding preserves constraints? **YES** - `ga_optimizer.py` validates constraints during chromosome generation and mutation

### Rapid Prototyping (Principle IV)
- [x] Using simplified models initially (not Mesa)? **YES** - Schemes use mathematical formulas in `data/schemes/*.yaml`, no agent-based simulation
- [x] 3-5 test scenarios sufficient for POC? **YES** - `config/scenarios/` contains representative scenarios (strait control, landing clearance, etc.)
- [x] Computational correctness prioritized over visualization? **YES** - Core algorithms in `modules/`, visualization is secondary in `utils/visualization.py`

### Documentation & Reproducibility (Principle V)
- [x] All indicators reference theoretical sources? **YES** - `config/indicators.yaml` includes literature references (Alberts 2000, Boyd 1987, etc.)
- [x] Configuration includes citations? **YES** - YAML config files have inline comments with methodology references
- [x] Output includes execution parameters? **YES** - `outputs/results/` includes GA params (population, generations, operators) with results
- [x] Code includes methodology docstrings? **YES** - All `modules/*.py` files will have docstrings linking to AHP/FCE/TOPSIS/GA methodology

**Constitution Check Result**: ✅ **ALL GATES PASS** - No violations, proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
ahp_fce_topsis/
├── config/                    # Configuration files
│   ├── indicators.yaml        # 15-indicator hierarchy with weights
│   ├── fuzzy_sets.yaml        # Linguistic term definitions (差/中/良/优)
│   └── scenarios/             # Scenario-specific configs
│       ├── strait_control.yaml
│       └── landing_clearance.yaml
├── modules/                   # Core algorithm implementations
│   ├── __init__.py
│   ├── ahp_module.py         # AHP weight calculation + CR validation
│   ├── fce_module.py         # Fuzzy comprehensive evaluation
│   ├── topsis_module.py      # TOPSIS ranking algorithm
│   ├── ga_optimizer.py       # Genetic algorithm integration
│   └── evaluator.py          # Main evaluation orchestrator
├── data/                      # Input data and expert judgments
│   ├── expert_judgments/      # AHP pairwise comparison matrices
│   │   ├── primary_capabilities.yaml
│   │   └── secondary_indicators/
│   │       ├── c1_indicators.yaml
│   │       ├── c2_indicators.yaml
│   │       ├── c3_indicators.yaml
│   │       ├── c4_indicators.yaml
│   │       └── c5_indicators.yaml
│   └── schemes/               # Combat system configuration data
│       ├── baseline_scheme.yaml
│       ├── scheme_a.yaml
│       └── scheme_b.yaml
├── utils/                     # Helper utilities
│   ├── __init__.py
│   ├── consistency_check.py  # AHP CR calculation
│   ├── normalization.py      # Vector normalization for TOPSIS
│   ├── validation.py         # Mathematical validation functions
│   └── visualization.py      # Chart generation (matplotlib)
├── outputs/                   # Generated results (git-ignored)
│   ├── results/               # Evaluation results (JSON/CSV)
│   ├── reports/               # Generated reports
│   └── plots/                 # Convergence curves, comparison charts
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests for each module
│   │   ├── test_ahp.py
│   │   ├── test_fce.py
│   │   ├── test_topsis.py
│   │   └── test_ga.py
│   ├── integration/           # Pipeline integration tests
│   │   ├── test_evaluation_pipeline.py
│   │   └── test_optimization_workflow.py
│   └── fixtures/              # Test data fixtures
│       ├── sample_matrices.yaml
│       └── sample_schemes.yaml
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata (optional)
└── README.md                  # Setup and usage instructions
```

**Structure Decision**: Single project layout selected based on:
- Command-line tool with programmatic API (no web/mobile components)
- All components share Python runtime and dependencies
- Modular structure aligns with Constitutional Principle I (separation of AHP/FCE/TOPSIS/GA)
- Configuration-driven approach supports Principle II (data-driven evaluation)
- Clear separation of algorithm code (`modules/`), data (`data/`, `config/`), and utilities (`utils/`)
- Test structure mirrors source structure for maintainability

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All constitutional requirements satisfied by design:
- Modular architecture with 5 independent modules
- Data-driven approach with YAML configuration
- Scientific rigor through mathematical validation
- Rapid prototyping with simplified simulation
- Documentation with literature references

---

## Phase 2: Implementation Planning Summary

### Phase 0: Research ✅ COMPLETE

**Artifacts Generated**:
- `research.md` - 7 key technical decisions documented with alternatives and rationales

**Key Decisions**:
1. AHP eigenvalue method for weight calculation
2. Discrete fuzzy membership vectors for FCE
3. Vector normalization for TOPSIS
4. PyGAD library for genetic algorithm
5. YAML configuration format
6. NumPy vectorization for performance
7. Fail-fast validation strategy

### Phase 1: Design & Contracts ✅ COMPLETE

**Artifacts Generated**:
- `data-model.md` - 6 entities fully specified with validation rules
- `contracts/module_interfaces.md` - 6 modules with 12+ function contracts
- `quickstart.md` - Comprehensive usage guide with 3 scenarios
- `CLAUDE.md` - Agent context updated with Python 3.8+ and file-based storage

**Design Highlights**:
- 15-indicator evaluation hierarchy (5 primary × 3 secondary)
- Single project structure (no web/mobile components)
- File-based persistence (YAML configs, JSON results)
- Modular pipeline: AHP → FCE → TOPSIS → GA
- Performance targets: <0.5s evaluation, <5min optimization

### Constitution Re-check ✅ ALL GATES PASS

All 5 constitutional principles satisfied:
- ✅ Modular Architecture - Independent modules with clear interfaces
- ✅ Data-Driven Evaluation - Version-controlled YAML configurations
- ✅ Scientific Rigor - CR validation, normalization checks, constraint enforcement
- ✅ Rapid Prototyping - Simplified simulation, 3-5 test scenarios
- ✅ Documentation - Literature references in all configs, audit logging

**No complexity violations** - Design adheres to constitutional standards without exceptions.

---

## Next Steps

### Ready for Implementation (`/speckit.tasks`)

The planning phase is complete. Next command generates actionable task list:

```bash
/speckit.tasks
```

This will produce `tasks.md` with implementation tasks organized by:
- **Phase 1: Setup** - Project structure, dependencies, configuration templates
- **Phase 2: Foundation** - Core utilities (validation, normalization, logging)
- **Phase 3: User Story 1** - AHP-FCE-TOPSIS evaluation pipeline (MVP)
- **Phase 4: User Story 2** - GA optimization integration
- **Phase 5: User Story 3** - Sensitivity analysis and validation
- **Phase 6: Polish** - Documentation, testing, performance tuning

### Implementation Roadmap (7-Day Timeline)

| Day | Focus | Deliverables |
|-----|-------|-------------|
| 1-2 | Setup + Foundation | Project structure, utils, test fixtures |
| 3-4 | User Story 1 (MVP) | AHP, FCE, TOPSIS modules + evaluator |
| 5 | User Story 2 | GA optimizer + fitness function integration |
| 6 | User Story 3 | Sensitivity analysis, validation reports |
| 7 | Testing + Polish | Integration tests, quickstart validation, documentation |

### Success Criteria Verification

Before deployment, validate against all 17 success criteria:
- SC-001 to SC-004: Evaluation accuracy & validity
- SC-005 to SC-008: Optimization performance
- SC-009 to SC-011: Validation & robustness
- SC-012 to SC-014: Research quality
- SC-015 to SC-017: Usability & workflow

---

## Planning Phase Complete

**Status**: ✅ **Ready for `/speckit.tasks`**

**Branch**: `001-ahp-fce-topsis-ga-system`

**Generated Artifacts**:
- `plan.md` (this file)
- `research.md` (technical decisions)
- `data-model.md` (entity schemas)
- `contracts/module_interfaces.md` (API contracts)
- `quickstart.md` (usage guide)
- `CLAUDE.md` (agent context)

**Total Documentation**: 6 files, ~500 lines of specifications

**Estimated Implementation**: 7 days for full system (MVP achievable in 4 days)
