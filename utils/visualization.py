"""
Visualization Utilities for AHP-FCE-TOPSIS-GA Evaluation System

Provides functions for generating charts and plots for evaluation results,
GA convergence, and sensitivity analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional
import os
from datetime import datetime


def plot_convergence(ga_results: Dict[str, Any], output_path: str) -> None:
    """
    Generate convergence plot for GA optimization results.

    Args:
        ga_results: Results from GA optimization
        output_path: Path to save plot
    """
    try:
        generation_history = ga_results.get('generation_history', {})

        if not generation_history.get('best_fitness'):
            print("No fitness history available for plotting")
            return

        plt.figure(figsize=(12, 8))

        generations = list(range(1, len(generation_history['best_fitness']) + 1))

        # Plot fitness evolution
        plt.subplot(2, 2, 1)
        plt.plot(generations, generation_history['best_fitness'], 'b-', linewidth=2, label='Best Fitness')
        plt.plot(generations, generation_history['avg_fitness'], 'r--', linewidth=1, label='Average Fitness')
        plt.xlabel('Generation')
        plt.ylabel('Fitness Score')
        plt.title('Fitness Evolution')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plot diversity
        plt.subplot(2, 2, 2)
        plt.plot(generations, generation_history['diversity'], 'g-', linewidth=2, label='Population Diversity')
        plt.xlabel('Generation')
        plt.ylabel('Diversity')
        plt.title('Population Diversity')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plot fitness improvement rate
        plt.subplot(2, 2, 3)
        if len(generation_history['best_fitness']) > 1:
            improvement_rates = []
            for i in range(1, len(generation_history['best_fitness'])):
                if generation_history['best_fitness'][i-1] > 0:
                    rate = (generation_history['best_fitness'][i] - generation_history['best_fitness'][i-1]) / generation_history['best_fitness'][i-1]
                    improvement_rates.append(rate)
                else:
                    improvement_rates.append(0)

            plt.plot(generations[1:], improvement_rates, 'm-', linewidth=1)
            plt.xlabel('Generation')
            plt.ylabel('Improvement Rate')
            plt.title('Fitness Improvement Rate')
            plt.grid(True, alpha=0.3)

        # Plot final fitness distribution
        plt.subplot(2, 2, 4)
        final_fitness = [sol['fitness'] for sol in generation_history['best_solutions'][-10:]]  # Last 10 generations
        if final_fitness:
            plt.bar(range(len(final_fitness)), final_fitness)
            plt.xlabel('Solution Index')
            plt.ylabel('Fitness')
            plt.title('Final Generation Fitness Distribution')
            plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Convergence plot saved to: {output_path}")

    except Exception as e:
        print(f"Error generating convergence plot: {e}")


def plot_comparison_chart(results_json: Dict[str, Any], output_path: str) -> None:
    """
    Generate bar chart comparing Ci scores across configurations.

    Args:
        results_json: Evaluation results dictionary
        output_path: Path to save plot
    """
    try:
        if 'individual_results' in results_json:
            # Batch evaluation results
            results = results_json['individual_results']
            scheme_ids = list(results.keys())
            ci_scores = [results[sid]['ci_score'] for sid in scheme_ids]
            ranks = [results[sid]['rank'] for sid in scheme_ids]
        else:
            # Single evaluation result
            scheme_ids = [results_json.get('scheme_id', 'Unknown')]
            ci_scores = [results_json.get('ci_score', 0)]
            ranks = [results_json.get('rank', 1)]

        # Sort by rank
        sorted_data = sorted(zip(scheme_ids, ci_scores, ranks), key=lambda x: x[2])
        scheme_ids, ci_scores, ranks = zip(*sorted_data)

        plt.figure(figsize=(10, 6))

        # Create color map based on rank
        colors = plt.cm.RdYlBu_r([r / max(ranks) for r in ranks])

        bars = plt.bar(range(len(scheme_ids)), ci_scores, color=colors)

        # Customize plot
        plt.xlabel('Configurations')
        plt.ylabel('Ci Score')
        plt.title('Configuration Performance Comparison')
        plt.xticks(range(len(scheme_ids)), scheme_ids, rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, ci_score in zip(bars, ci_scores):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{ci_score:.3f}', ha='center', va='bottom')

        # Note: Color bar removed to avoid layout issues with small datasets

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Comparison chart saved to: {output_path}")

    except Exception as e:
        print(f"Error generating comparison chart: {e}")


def plot_radar_chart(configuration_results: Dict[str, Any],
                    indicator_config: Dict[str, Any],
                    output_path: str) -> None:
    """
    Generate radar chart showing multi-dimensional capability profiles.

    Args:
        configuration_results: Dictionary with configuration results
        indicator_config: Indicator configuration
        output_path: Path to save plot
    """
    try:
        from matplotlib.patches import Circle
        import matplotlib.patches as mpatches

        # Extract indicator values and names
        if isinstance(configuration_results, dict) and 'indicator_values' in configuration_results:
            indicator_values = configuration_results['indicator_values']
        else:
            print("No indicator values found for radar chart")
            return

        # Get indicator names from config
        secondary_indicators = indicator_config.get('secondary_indicators', {})
        indicator_names = [ind_data.get('name', f'Indicator_{i}')
                          for i, (ind_id, ind_data) in enumerate(secondary_indicators.items())
                          if i < len(indicator_values)]

        # Ensure we have the right number of indicators
        if len(indicator_names) != len(indicator_values):
            # Fallback to generic names
            indicator_names = [f'Indicator_{i+1}' for i in range(len(indicator_values))]

        # Number of variables
        N = len(indicator_values)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        indicator_values = indicator_values + [indicator_values[0]]  # Complete the circle
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # Plot the radar chart
        ax.plot(angles, indicator_values, 'o-', linewidth=2, label='Configuration Profile')
        ax.fill(angles, indicator_values, alpha=0.25)

        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(indicator_names)
        ax.set_ylim(0, 1)

        # Add grid and title
        ax.grid(True)
        ax.set_title("Multi-Dimensional Capability Profile", size=16, pad=20)

        # Add legend
        scheme_name = configuration_results.get('scheme_id', 'Configuration')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Radar chart saved to: {output_path}")

    except Exception as e:
        print(f"Error generating radar chart: {e}")


def plot_sensitivity_results(sensitivity_json: Dict[str, Any], output_path: str) -> None:
    """
    Visualize ranking stability and Ci variation distributions from sensitivity analysis.

    Args:
        sensitivity_json: Sensitivity analysis results
        output_path: Path to save plot
    """
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Sensitivity Analysis Results', fontsize=16)

        # Plot 1: Ranking stability over iterations
        ax1 = axes[0, 0]
        iteration_results = sensitivity_json.get('iteration_results', [])
        if iteration_results:
            iterations = [result['iteration'] for result in iteration_results]
            baseline_ranking = sensitivity_json.get('baseline_ranking', [])

            # Track if ranking changed from baseline
            ranking_changes = []
            for result in iteration_results:
                current_ranking = result['rankings']
                changed = current_ranking != baseline_ranking
                ranking_changes.append(1 if changed else 0)

            ax1.plot(iterations, ranking_changes, 'r-', alpha=0.7)
            ax1.fill_between(iterations, ranking_changes, alpha=0.3, color='red')
            ax1.set_xlabel('Iteration')
            ax1.set_ylabel('Ranking Changed (1=Yes, 0=No)')
            ax1.set_title('Ranking Stability Over Iterations')
            ax1.grid(True, alpha=0.3)

            # Add stability percentage
            stability_pct = sensitivity_json.get('summary_stats', {}).get('ranking_stability_pct', 0)
            ax1.text(0.02, 0.98, f'Stability: {stability_pct:.1f}%',
                    transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # Plot 2: CI variation distribution for each alternative
        ax2 = axes[0, 1]
        ci_variations = sensitivity_json.get('ci_variations', {})

        if ci_variations:
            alternatives = list(ci_variations.keys())
            variation_pcts = [ci_variations[alt]['variation_pct'] * 100 for alt in alternatives]

            bars = ax2.bar(alternatives, variation_pcts, color='skyblue', alpha=0.7)
            ax2.set_xlabel('Alternatives')
            ax2.set_ylabel('CI Variation (%)')
            ax2.set_title('CI Score Variation by Alternative')
            ax2.grid(True, alpha=0.3, axis='y')
            ax2.tick_params(axis='x', rotation=45)

            # Add value labels
            for bar, var_pct in zip(bars, variation_pcts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(variation_pcts) * 0.01,
                        f'{var_pct:.2f}%', ha='center', va='bottom')

        # Plot 3: CI score distribution for top alternative
        ax3 = axes[1, 0]
        if iteration_results:
            # Get CI scores for first alternative across all iterations
            all_ci_scores = []
            for result in iteration_results:
                ci_scores = result.get('ci_scores', [])
                if ci_scores:
                    all_ci_scores.append(ci_scores[0])  # First alternative

            if all_ci_scores:
                ax3.hist(all_ci_scores, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
                ax3.set_xlabel('CI Score')
                ax3.set_ylabel('Frequency')
                ax3.set_title('CI Score Distribution (Alternative 1)')
                ax3.grid(True, alpha=0.3)

                # Add statistics
                mean_ci = np.mean(all_ci_scores)
                std_ci = np.std(all_ci_scores)
                ax3.axvline(mean_ci, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_ci:.4f}')
                ax3.axvline(mean_ci + std_ci, color='orange', linestyle='--', alpha=0.7, label=f'±1σ: {std_ci:.4f}')
                ax3.axvline(mean_ci - std_ci, color='orange', linestyle='--', alpha=0.7)
                ax3.legend()

        # Plot 4: Summary statistics
        ax4 = axes[1, 1]
        ax4.axis('off')

        summary_stats = sensitivity_json.get('summary_stats', {})

        # Create summary text
        summary_text = f"""
        Sensitivity Analysis Summary

        Iterations Completed: {summary_stats.get('iterations_completed', 0)}
        Ranking Stability: {summary_stats.get('ranking_stability_pct', 0):.1f}%
        Max CI Variation: {summary_stats.get('max_ci_variation_pct', 0):.2f}%
        Iterations with Changes: {summary_stats.get('iterations_with_ranking_changes', 0)}

        Perturbation Level: ±{sensitivity_json.get('perturbation_pct', 0) * 100:.1f}%
        """

        ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=12,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Sensitivity analysis plot saved to: {output_path}")

    except Exception as e:
        print(f"Error generating sensitivity analysis plot: {e}")


def create_comprehensive_report(evaluation_results: Dict[str, Any],
                              sensitivity_results: Optional[Dict[str, Any]] = None,
                              ga_results: Optional[Dict[str, Any]] = None,
                              output_dir: str = "outputs/reports") -> None:
    """
    Create comprehensive evaluation report with all visualizations.

    Args:
        evaluation_results: Main evaluation results
        sensitivity_results: Optional sensitivity analysis results
        ga_results: Optional GA optimization results
        output_dir: Directory to save report files
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"Creating comprehensive evaluation report...")
        print(f"Output directory: {output_dir}")

        # Generate comparison chart
        if evaluation_results:
            comparison_path = os.path.join(output_dir, f"comparison_chart_{timestamp}.png")
            plot_comparison_chart(evaluation_results, comparison_path)

        # Generate sensitivity analysis plots
        if sensitivity_results:
            sensitivity_path = os.path.join(output_dir, f"sensitivity_analysis_{timestamp}.png")
            plot_sensitivity_results(sensitivity_results, sensitivity_path)

        # Generate GA convergence plot
        if ga_results:
            convergence_path = os.path.join(output_dir, f"ga_convergence_{timestamp}.png")
            plot_convergence(ga_results, convergence_path)

        # Generate radar charts for each configuration
        if evaluation_results and 'individual_results' in evaluation_results:
            indicator_config = evaluation_results.get('indicator_config', {})

            for scheme_id, result in evaluation_results['individual_results'].items():
                radar_path = os.path.join(output_dir, f"radar_{scheme_id}_{timestamp}.png")
                plot_radar_chart(result, indicator_config, radar_path)

        print(f"Comprehensive report created successfully!")

    except Exception as e:
        print(f"Error creating comprehensive report: {e}")


if __name__ == "__main__":
    # Example usage and testing
    print("Testing Visualization Utilities")

    # Test data for convergence plot
    test_ga_results = {
        'generation_history': {
            'best_fitness': [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.42, 0.43, 0.44],
            'avg_fitness': [0.08, 0.12, 0.16, 0.2, 0.24, 0.28, 0.32, 0.35, 0.37, 0.38],
            'diversity': [0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.38, 0.35, 0.33, 0.3],
            'best_solutions': [
                {'generation': i+1, 'fitness': 0.1 + i*0.03, 'solution': [1, 2, 3], 'decoded_config': {}}
                for i in range(10)
            ]
        }
    }

    # Test convergence plot
    plot_convergence(test_ga_results, "test_convergence.png")
    print("Test convergence plot created: test_convergence.png")

    # Test data for comparison chart
    test_results = {
        'individual_results': {
            'scheme_A': {'ci': 0.75, 'rank': 1},
            'scheme_B': {'ci': 0.60, 'rank': 2},
            'scheme_C': {'ci': 0.45, 'rank': 3}
        }
    }

    # Test comparison chart
    plot_comparison_chart(test_results, "test_comparison.png")
    print("Test comparison chart created: test_comparison.png")