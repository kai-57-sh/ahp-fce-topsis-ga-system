#!/usr/bin/env python3
"""
AHP-FCE-TOPSIS-GA Evaluation System - Command Line Interface

Main entry point for evaluating combat system configurations using
AHP-FCE-TOPSIS methodology and genetic algorithm optimization.
"""

import argparse
import sys
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from modules.evaluator import evaluate_single_scheme, evaluate_batch, EvaluatorError
from modules.ahp_module import AHPConsistencyError
from utils.validation import ValidationError


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}")
        sys.exit(1)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        sys.exit(1)


def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to JSON file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def convert_numpy_types(obj):
        """Convert numpy types to native Python types for JSON serialization."""
        if hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(v) for v in obj]
        elif isinstance(obj, tuple):
            return tuple(convert_numpy_types(v) for v in obj)
        else:
            return obj

    try:
        # Convert numpy types before saving
        json_data = convert_numpy_types(data)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {file_path}")
    except Exception as e:
        print(f"Error saving results to {file_path}: {e}")
        sys.exit(1)


def cmd_evaluate(args) -> None:
    """Handle 'evaluate' command."""
    print("Starting evaluation...")

    # Load configurations
    print("Loading configurations...")
    indicator_config = load_yaml_file(args.indicators)
    fuzzy_config = load_yaml_file(args.fuzzy_sets)

    # Load expert judgments
    expert_judgments = {
        'primary_capabilities_file': args.expert_judgments,
        'secondary_indicators_dir': os.path.join(os.path.dirname(args.expert_judgments), 'secondary_indicators')
    }

    # Load scenario if provided
    scenario_context = None
    if args.scenario:
        print(f"Loading operational scenario: {args.scenario}")
        scenario_context = load_yaml_file(args.scenario)
        print(f"Loaded scenario: {scenario_context.get('scenario_name', 'Unknown')}")
    else:
        print("No scenario specified - using generic evaluation")

    # Load schemes and integrate scenario context
    schemes = []
    for scheme_file in args.schemes:
        scheme_data = load_yaml_file(scheme_file)

        # Integrate scenario context into scheme if scenario is provided
        if scenario_context:
            scheme_data['scenario_context'] = scenario_context.get('scenario_id', 'generic')
            scheme_data['mission_objectives'] = scenario_context.get('mission_objectives', {})
            scheme_data['threat_environment'] = scenario_context.get('threat_environment', {})
            scheme_data['scenario_config'] = scenario_context  # 保存完整场景配置

            # Apply scenario-specific constraints if not overridden in scheme
            if 'operational_constraints' not in scheme_data:
                scheme_data['operational_constraints'] = scenario_context.get('operational_constraints', {})

        schemes.append(scheme_data)

    print(f"Loaded {len(schemes)} scheme(s) for evaluation")

    try:
        if args.batch and len(schemes) > 1:
            # Batch evaluation
            print("Performing batch evaluation...")
            results = evaluate_batch(schemes, indicator_config, fuzzy_config, expert_judgments)

            # Print summary
            print("\n" + "="*60)
            print("EVALUATION RESULTS")
            print("="*60)
            print(f"Total schemes evaluated: {results['num_schemes']}")
            print(f"Best scheme: {results['best_scheme']['scheme_id']} (Ci: {results['best_scheme']['Ci_score']:.4f})")

            print("\nRankings:")
            sorted_results = sorted(
                results['individual_results'].items(),
                key=lambda x: x[1]['rank']
            )
            for rank, (scheme_id, result) in enumerate(sorted_results, 1):
                print(f"  {rank}. {scheme_id}: Ci = {result['Ci']:.4f}")

            # Save results
            if args.output:
                save_json_file(results, args.output)

        else:
            # Single scheme evaluation
            if len(schemes) > 1:
                print("\nNote: Running individual evaluations (each scheme vs baseline)")
                print("      For comparative ranking between schemes, use --batch flag")

            for i, scheme in enumerate(schemes, 1):
                print(f"\nEvaluating scheme {i}/{len(schemes)}: {scheme['scheme_id']}")

                result = evaluate_single_scheme(scheme, indicator_config, fuzzy_config, expert_judgments)

                print(f"  Ci Score: {result['ci_score']:.4f}")
                print(f"  Rank: {result['rank']}")

                # Show baseline comparison for single schemes
                metadata = result.get('evaluation_metadata', {})
                if 'performance_vs_baseline' in metadata:
                    print(f"  vs Baseline: {metadata['performance_vs_baseline']} (Baseline Ci: {metadata['baseline_ci_score']:.3f})")

                print(f"  Validation: {'PASSED' if result.get('evaluation_metadata', {}).get('validation_passed', False) else 'FAILED'}")

                # Save individual result
                if args.output:
                    if len(schemes) == 1:
                        save_json_file(result, args.output)
                    else:
                        # Generate filename for each scheme
                        base_path = args.output.rsplit('.', 1)[0]
                        extension = args.output.rsplit('.', 1)[1] if '.' in args.output else 'json'
                        individual_output = f"{base_path}_{scheme['scheme_id']}.{extension}"
                        save_json_file(result, individual_output)

        print("\nEvaluation completed successfully!")

    except AHPConsistencyError as e:
        print(f"\nError: AHP consistency validation failed")
        print(f"Details: {e}")
        print("Please check expert judgment matrices for consistency.")
        sys.exit(1)

    except ValidationError as e:
        print(f"\nError: Validation failed")
        print(f"Details: {e}")
        sys.exit(1)

    except EvaluatorError as e:
        print(f"\nError: Evaluation failed")
        print(f"Details: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


def cmd_optimize(args) -> None:
    """Handle 'optimize' command."""
    print("Starting genetic algorithm optimization...")

    # Load configurations
    print("Loading scenario configuration...")
    scenario_config = load_yaml_file(args.scenario)
    indicator_config = load_yaml_file(args.indicators)
    fuzzy_config = load_yaml_file(args.fuzzy_sets)

    # Load expert judgments
    expert_judgments = args.expert_judgments

    # GA parameters
    ga_params = {
        'population_size': args.population,
        'num_generations': args.generations,
        'num_parents_mating': 4,
        'parent_selection_type': 'tournament',
        'crossover_type': 'single_point',
        'mutation_type': 'random',
        'mutation_percent_genes': 20,
        'keep_parents': 1
    }

    # Extract constraints from scenario
    constraints = scenario_config.get('constraints', {})
    constraint_spec = constraints.copy()  # Use all constraints from scenario

    # Add any missing default constraints
    if 'deployment_bounds' not in constraint_spec:
        constraint_spec['deployment_bounds'] = {
            'min_x': 20, 'max_x': 80,
            'min_y': 20, 'max_y': 80
        }

    try:
        # Import GA optimizer
        from modules.ga_optimizer import optimize_configuration, plot_convergence, GAError

        # Run optimization
        results = optimize_configuration(
            scenario_config, ga_params, constraint_spec,
            indicator_config, fuzzy_config, expert_judgments
        )

        # Display results
        print("\n" + "="*60)
        print("OPTIMIZATION RESULTS")
        print("="*60)
        print(f"Best Configuration Fitness: {results['best_fitness']:.4f}")
        print(f"Total Generations: {results['convergence_info']['total_generations']}")
        print(f"Converged: {results['convergence_info']['converged']}")
        print(f"Monotonic Improvement: {results['convergence_info']['monotonic_improvement']}")
        print(f"Final Population Diversity: {results['convergence_info']['final_diversity']:.3f}")

        # Display best configuration
        best_config = results['best_configuration']
        print(f"\nBest Configuration:")
        print(f"  Total Platforms: {sum(data['count'] for data in best_config['platform_inventory'].values())}")
        print(f"  Deployment: {best_config['deployment_plan'].get('primary_sector', {}).get('coordinates', 'N/A')}")
        print(f"  Estimated Cost: ${best_config['operational_constraints']['max_budget_million_usd']:.1f}M")

        # Display final evaluation
        final_eval = results['final_evaluation']
        print(f"\nFinal Evaluation:")
        print(f"  Ci Score: {final_eval['ci_score']:.4f}")
        print(f"  Rank: {final_eval['rank']}")
        print(f"  Validation: {'PASSED' if final_eval.get('evaluation_metadata', {}).get('validation_passed', False) else 'FAILED'}")

        # Save results
        if args.output:
            save_json_file(results, args.output)

            # Generate convergence plot
            plot_path = args.output.rsplit('.', 1)[0] + '_convergence.png'
            plot_convergence(results, plot_path)

        print("\nOptimization completed successfully!")

    except Exception as e:
        print(f"\nError: GA optimization failed")
        print(f"Details: {e}")
        sys.exit(1)


def cmd_sensitivity(args) -> None:
    """Handle 'sensitivity' command."""
    print("Starting sensitivity analysis...")

    try:
        # Load baseline results
        print(f"Loading baseline results: {args.baseline_results}")
        baseline_results = load_json_file(args.baseline_results)

        # Import sensitivity analysis function
        from utils.validation import perform_sensitivity_analysis

        # Perform sensitivity analysis
        print(f"Running sensitivity analysis with {args.iterations} iterations...")
        print(f"Perturbation level: ±{args.perturbation * 100:.1f}%")

        sensitivity_results = perform_sensitivity_analysis(
            baseline_results,
            perturbation_pct=args.perturbation,
            iterations=args.iterations
        )

        # Analyze ranking stability
        stability_pct = sensitivity_results['summary_stats']['ranking_stability_pct']
        max_variation = sensitivity_results['summary_stats']['max_ci_variation_pct']

        print("\n" + "="*60)
        print("SENSITIVITY ANALYSIS RESULTS")
        print("="*60)
        print(f"Ranking Stability: {stability_pct:.1f}%")
        print(f"Max CI Variation: {max_variation:.2f}%")
        print(f"Iterations with Ranking Changes: {sensitivity_results['summary_stats']['iterations_with_ranking_changes']}/{args.iterations}")

        # Check success criteria
        ranking_stable = stability_pct >= 80.0
        ci_variation_acceptable = max_variation <= 10.0

        print(f"\nSuccess Criteria Validation:")
        print(f"  Ranking Stability (≥80%): {'✓ PASS' if ranking_stable else '✗ FAIL'} ({stability_pct:.1f}%)")
        print(f"  CI Variation (≤10%): {'✓ PASS' if ci_variation_acceptable else '✗ FAIL'} ({max_variation:.2f}%)")

        # Show detailed results for top alternatives
        baseline_ranking = sensitivity_results['baseline_ranking']
        print(f"\nDetailed CI Variations:")
        for alt_id, variation_data in sensitivity_results['ci_variations'].items():
            alt_index = int(alt_id.split('_')[1]) - 1
            baseline_rank = baseline_ranking[alt_index] if alt_index < len(baseline_ranking) else 0
            variation_pct = variation_data['variation_pct'] * 100

            print(f"  {alt_id} (Baseline Rank {baseline_rank}):")
            print(f"    Baseline CI: {variation_data['baseline_ci']:.4f}")
            print(f"    Mean CI: {variation_data['mean_ci']:.4f}")
            print(f"    Variation: ±{variation_pct:.2f}%")

        # Save results
        if args.output:
            save_json_file(sensitivity_results, args.output)

        print(f"\nSensitivity analysis completed successfully!")
        if ranking_stable and ci_variation_acceptable:
            print("✓ Results are robust to weight perturbations")
        else:
            print("⚠ Results show sensitivity to weight changes - consider review")

    except Exception as e:
        print(f"\nError: Sensitivity analysis failed")
        print(f"Details: {e}")
        sys.exit(1)


def cmd_validate(args) -> None:
    """Handle 'validate' command."""
    print("Validating configuration files...")

    try:
        if args.scheme:
            # Validate scheme configuration
            print(f"Validating scheme: {args.scheme}")
            scheme_data = load_yaml_file(args.scheme)
            from utils.validation import validate_scheme_config
            validation = validate_scheme_config(scheme_data)

            if validation['is_valid']:
                print("✓ Scheme configuration is valid")
            else:
                print("✗ Scheme configuration validation failed:")
                for error in validation['errors']:
                    print(f"  - {error}")
                for warning in validation['warnings']:
                    print(f"  Warning: {warning}")

        elif args.ahp_matrix:
            # Validate AHP matrix
            print(f"Validating AHP matrix: {args.ahp_matrix}")
            matrix_data = load_yaml_file(args.ahp_matrix)
            from modules.ahp_module import load_judgment_matrix, calculate_weights

            loaded_data = load_judgment_matrix(args.ahp_matrix)
            matrix = loaded_data['matrix']
            import numpy as np
            matrix_array = np.array(matrix)

            result = calculate_weights(matrix_array)
            print(f"✓ AHP matrix is valid")
            print(f"  Consistency Ratio (CR): {result['CR']:.4f}")
            print(f"  Lambda max: {result['lambda_max']:.4f}")
            print(f"  Valid: {result['valid']}")

        else:
            print("Error: Must specify either --scheme or --ahp-matrix")
            sys.exit(1)

    except Exception as e:
        print(f"Validation failed: {e}")
        sys.exit(1)


def cmd_visualize(args) -> None:
    """Handle 'visualize' command."""
    print(f"Generating {args.plot_type} plot...")

    try:
        # Load input data
        input_data = load_json_file(args.input)

        # Import visualization functions
        from utils.visualization import (
            plot_convergence, plot_comparison_chart, plot_radar_chart,
            plot_sensitivity_results
        )

        # Generate default output path if not provided
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"outputs/plots/{args.plot_type}_{timestamp}.png"

        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate appropriate plot
        if args.plot_type == 'convergence':
            plot_convergence(input_data, output_path)
        elif args.plot_type == 'comparison':
            plot_comparison_chart(input_data, output_path)
        elif args.plot_type == 'radar':
            if not args.indicator_config:
                print("Error: --indicator-config required for radar plots")
                sys.exit(1)
            indicator_config = load_yaml_file(args.indicator_config)
            plot_radar_chart(input_data, indicator_config, output_path)
        elif args.plot_type == 'sensitivity':
            plot_sensitivity_results(input_data, output_path)

        print(f"Plot saved to: {output_path}")

    except Exception as e:
        print(f"Error generating plot: {e}")
        sys.exit(1)


def cmd_report(args) -> None:
    """Handle 'report' command."""
    print("Generating comprehensive evaluation report...")

    try:
        # Load evaluation results
        results = load_json_file(args.results)

        # Generate default output path if not provided
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"outputs/reports/comprehensive_report_{timestamp}.{args.format}"

        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Import report generation function
        from utils.reporting import generate_comprehensive_report

        # Generate report
        report_data = generate_comprehensive_report(
            results=results,
            include_methodology=args.include_methodology,
            include_sensitivity=args.include_sensitivity,
            format_type=args.format,
            template_path=args.template
        )

        # Save report
        if args.format == 'md':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_data)
        elif args.format == 'pdf':
            # For PDF, we'd use matplotlib to save figures and combine with text
            # For now, save as markdown with .pdf extension (placeholder)
            with open(output_path.replace('.pdf', '.md'), 'w', encoding='utf-8') as f:
                f.write(report_data)
            print(f"Note: PDF generation requires additional dependencies. Saved as Markdown instead.")

        print(f"Report saved to: {output_path}")

        # Print summary
        if 'individual_results' in results:
            num_schemes = len(results['individual_results'])
            print(f"Report includes analysis of {num_schemes} configuration(s)")

        if args.include_methodology:
            print("✓ Methodology section included")

        if args.include_sensitivity:
            print("✓ Sensitivity analysis section included")

    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


def create_sample_configs() -> None:
    """Create sample configuration files for testing."""
    print("Creating sample configuration files...")

    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)

    # Sample evaluation command
    sample_cmd = (
        "python main.py evaluate \\\n"
        "    --schemes data/schemes/baseline_scheme.yaml data/schemes/scheme_a.yaml \\\n"
        "    --indicators config/indicators.yaml \\\n"
        "    --fuzzy-sets config/fuzzy_sets.yaml \\\n"
        "    --expert-judgments data/expert_judgments/primary_capabilities.yaml \\\n"
        "    --batch \\\n"
        "    --output outputs/evaluation_results.json"
    )

    print("\nSample command for evaluation:")
    print(sample_cmd)

    # Sample validation command
    validation_cmd = (
        "python main.py validate \\\n"
        "    --scheme data/schemes/baseline_scheme.yaml"
    )

    print("\nSample command for validation:")
    print(validation_cmd)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AHP-FCE-TOPSIS-GA Evaluation System for Combat System Configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate single scheme
  python main.py evaluate --schemes data/schemes/baseline_scheme.yaml --output results.json

  # Evaluate multiple schemes with batch ranking
  python main.py evaluate --schemes data/schemes/*.yaml --batch --output results.json

  # Validate configuration
  python main.py validate --scheme data/schemes/baseline_scheme.yaml

  # Validate AHP matrix
  python main.py validate --ahp-matrix data/expert_judgments/primary_capabilities.yaml

For more information, see README.md
        """
    )

    parser.add_argument('--version', action='version', version='AHP-FCE-TOPSIS-GA 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate combat system configurations')
    eval_parser.add_argument('--schemes', nargs='+', required=True,
                             help='Path(s) to scheme YAML files')
    eval_parser.add_argument('--scenario',
                             help='Path to operational scenario configuration (optional - provides context-specific evaluation)')
    eval_parser.add_argument('--indicators', default='config/indicators.yaml',
                             help='Path to indicators configuration (default: config/indicators.yaml)')
    eval_parser.add_argument('--fuzzy-sets', default='config/fuzzy_sets.yaml',
                             help='Path to fuzzy sets configuration (default: config/fuzzy_sets.yaml)')
    eval_parser.add_argument('--expert-judgments', default='data/expert_judgments/primary_capabilities.yaml',
                             help='Path to primary capabilities AHP matrix (default: data/expert_judgments/primary_capabilities.yaml)')
    eval_parser.add_argument('--batch', action='store_true',
                             help='Perform batch evaluation and ranking')
    eval_parser.add_argument('--output', help='Output file path (JSON format)')

    # Optimize command
    opt_parser = subparsers.add_parser('optimize', help='Optimize configuration using genetic algorithm')
    opt_parser.add_argument('--scenario', required=True, help='Path to scenario configuration')
    opt_parser.add_argument('--indicators', default='config/indicators.yaml', help='Path to indicators configuration (default: config/indicators.yaml)')
    opt_parser.add_argument('--fuzzy-sets', default='config/fuzzy_sets.yaml', help='Path to fuzzy sets configuration (default: config/fuzzy_sets.yaml)')
    opt_parser.add_argument('--expert-judgments', default='data/expert_judgments/primary_capabilities.yaml', help='Path to expert judgments (default: data/expert_judgments/primary_capabilities.yaml)')
    opt_parser.add_argument('--population', type=int, default=20, help='Population size (default: 20)')
    opt_parser.add_argument('--generations', type=int, default=50, help='Number of generations (default: 50)')
    opt_parser.add_argument('--output', help='Output file path (JSON format)')

    # Sensitivity command
    sens_parser = subparsers.add_parser('sensitivity', help='Perform sensitivity analysis')
    sens_parser.add_argument('--baseline-results', required=True, help='Path to baseline evaluation results JSON file')
    sens_parser.add_argument('--perturbation', type=float, default=0.2, help='Weight perturbation amount (default: 0.2)')
    sens_parser.add_argument('--iterations', type=int, default=100, help='Number of iterations (default: 100)')
    sens_parser.add_argument('--output', help='Output file path (JSON format)')

    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualization plots')
    viz_parser.add_argument('--plot-type', required=True,
                           choices=['convergence', 'comparison', 'radar', 'sensitivity'],
                           help='Type of plot to generate')
    viz_parser.add_argument('--input', required=True, help='Input JSON file path')
    viz_parser.add_argument('--output', help='Output file path (optional)')
    viz_parser.add_argument('--indicator-config', help='Indicator config file (required for radar plots)')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate comprehensive evaluation report')
    report_parser.add_argument('--results', required=True, help='Path to evaluation results JSON file')
    report_parser.add_argument('--include-methodology', action='store_true', help='Include methodology section')
    report_parser.add_argument('--include-sensitivity', action='store_true', help='Include sensitivity analysis if available')
    report_parser.add_argument('--format', choices=['md', 'pdf'], default='md', help='Report format (default: md)')
    report_parser.add_argument('--output', help='Output file path (auto-generated if not provided)')
    report_parser.add_argument('--template', help='Custom template file (optional)')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate configuration files')
    val_group = val_parser.add_mutually_exclusive_group(required=True)
    val_group.add_argument('--scheme', help='Path to scheme YAML file to validate')
    val_group.add_argument('--ahp-matrix', help='Path to AHP matrix YAML file to validate')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Create sample configuration files')
    setup_parser.set_defaults(func=lambda args: create_sample_configs())

    # Set function for each command
    eval_parser.set_defaults(func=cmd_evaluate)
    opt_parser.set_defaults(func=cmd_optimize)
    sens_parser.set_defaults(func=cmd_sensitivity)
    viz_parser.set_defaults(func=cmd_visualize)
    report_parser.set_defaults(func=cmd_report)
    val_parser.set_defaults(func=cmd_validate)

    # Parse arguments
    args = parser.parse_args()

    # Check if command was provided
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()