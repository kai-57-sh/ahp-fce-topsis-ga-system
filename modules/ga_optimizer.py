"""
GA (Genetic Algorithm) Optimizer Module

Implements genetic algorithm optimization for discovering optimal combat system
configurations using PyGAD library integrated with AHP-FCE-TOPSIS evaluation pipeline.
"""

import numpy as np
import pygad
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
import json
import yaml
from datetime import datetime

from modules.evaluator import evaluate_single_scheme
from utils.validation import AuditLogger


class GAError(Exception):
    """Base exception for GA optimizer module."""
    pass


class ConstraintError(GAError):
    """Raised when constraints are violated."""
    pass


def decode_chromosome(chromosome: np.ndarray,
                     gene_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decode chromosome array to CombatSystemConfiguration dictionary format.

    Args:
        chromosome: Gene array representing configuration
        gene_config: Configuration defining gene structure and ranges

    Returns:
        Dictionary containing decoded configuration

    Raises:
        GAError: If chromosome decoding fails
    """
    try:
        configuration = {
            'scheme_id': 'ga_generated',
            'scheme_name': 'GA Optimized Configuration',
            'platform_inventory': {},
            'deployment_plan': {},
            'task_assignments': {},
            'operational_constraints': {},
            'simulation_parameters': {}
        }

        # Decode platform counts
        platform_types = gene_config['platform_types']
        for i, platform_type in enumerate(platform_types):
            count = int(chromosome[i])
            configuration['platform_inventory'][platform_type] = {
                'count': count,
                'types': {}  # Simplified for prototype
            }

        # Decode deployment coordinates
        num_deployment_zones = gene_config.get('num_deployment_zones', 1)
        start_idx = len(platform_types)

        if num_deployment_zones == 1:
            # Single deployment zone
            x_coord = chromosome[start_idx]
            y_coord = chromosome[start_idx + 1]
            configuration['deployment_plan']['primary_sector'] = {
                'coordinates': [x_coord, y_coord],
                'radius_km': gene_config.get('deployment_radius', 50)
            }
        else:
            # Multiple deployment zones
            configuration['deployment_plan']['secondary_sectors'] = []
            for i in range(num_deployment_zones):
                idx = start_idx + i * 2
                if idx + 1 < len(chromosome):
                    x_coord = chromosome[idx]
                    y_coord = chromosome[idx + 1]
                    configuration['deployment_plan']['secondary_sectors'].append({
                        'coordinates': [x_coord, y_coord],
                        'radius_km': gene_config.get('deployment_radius', 50)
                    })

        # Decode task assignments
        task_types = gene_config.get('task_types', ['surveillance', 'anti_submarine', 'mine_countermeasures'])
        task_start_idx = start_idx + num_deployment_zones * 2

        for i, task_type in enumerate(task_types):
            if task_start_idx + i < len(chromosome):
                assigned_platforms = int(chromosome[task_start_idx + i])
                configuration['task_assignments'][f'{task_type}_mission'] = {
                    'assigned_platforms': assigned_platforms,
                    'priority': 'high' if i == 0 else 'medium'
                }

        # Calculate operational constraints
        total_platforms = sum(config['count'] for config in configuration['platform_inventory'].values())
        base_budget = 2.5 * total_platforms  # Simplified cost calculation

        configuration['operational_constraints'] = {
            'total_platforms': total_platforms,
            'max_budget_million_usd': base_budget * 1.2,  # 20% buffer
            'deployment_area_km2': 5000 * (total_platforms / 10.0),
            'endurance_hours': 72,
            'communication_range_km': 100
        }

        # Generate simulation parameters based on decoded values
        configuration['simulation_parameters'] = {
            'detection_range_factor': 1.0 + (total_platforms - 10) * 0.05,
            'coordination_efficiency': 0.8 - (total_platforms - 10) * 0.01,
            'weapon_effectiveness': 0.85,
            'network_bandwidth_mbps': 100 + (total_platforms - 10) * 10,
            'stealth_factor': 0.7
        }

        return configuration

    except Exception as e:
        raise GAError(f"Failed to decode chromosome: {e}")


def validate_constraints(configuration: Dict[str, Any],
                        constraints: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration against operational constraints.

    Args:
        configuration: Configuration to validate
        constraints: Constraint specifications

    Returns:
        Dictionary with validation results

    Raises:
        ConstraintError: If constraints are violated
    """
    validation_result = {
        'valid': True,
        'violations': [],
        'warnings': []
    }

    try:
        # Check platform count constraints
        platform_inventory = configuration.get('platform_inventory', {})
        total_platforms = sum(data.get('count', 0) for data in platform_inventory.values())

        # Extract platform limits from constraints (support both old and new formats)
        platform_limits = constraints.get('platform_limits', {})
        if platform_limits:
            min_platforms = platform_limits.get('total_platforms', {}).get('min', 1)
            max_platforms = platform_limits.get('total_platforms', {}).get('max', 30)
        else:
            min_platforms = constraints.get('min_platforms', 1)
            max_platforms = constraints.get('max_platforms', 30)  # Increased to match gene encoding

        if total_platforms < min_platforms:
            validation_result['violations'].append(f"Too few platforms: {total_platforms} < {min_platforms}")
            validation_result['valid'] = False

        if total_platforms > max_platforms:
            validation_result['warnings'].append(f"Many platforms: {total_platforms} > {max_platforms}")
            # Changed to warning to allow GA exploration

        # Check budget constraints with proper cost calculation
        budget_constraints = constraints.get('budget', {})
        if budget_constraints:
            max_budget = budget_constraints.get('max_budget_million_usd', 100.0)
            cost_per_platform = budget_constraints.get('cost_per_platform', {})

            # Calculate actual cost based on platform types
            estimated_cost = 0.0
            for platform_type, data in platform_inventory.items():
                count = data.get('count', 0)
                # Map platform type to cost category
                if 'patrol' in platform_type.lower():
                    cost_per = cost_per_platform.get('patrol_usv', 2.5)
                elif 'surveillance' in platform_type.lower():
                    cost_per = cost_per_platform.get('surveillance_usv', 3.0)
                elif 'strike' in platform_type.lower():
                    cost_per = cost_per_platform.get('strike_usv', 4.0)
                elif 'attack' in platform_type.lower():
                    cost_per = cost_per_platform.get('attack_uuv', 5.0)
                elif 'reconnaissance' in platform_type.lower():
                    cost_per = cost_per_platform.get('reconnaissance_uuv', 2.0)
                else:
                    cost_per = 2.5  # Default cost
                estimated_cost += count * cost_per
        else:
            max_budget = constraints.get('max_budget_million_usd', 100.0)
            estimated_cost = total_platforms * 2.5  # Fallback to simplified calculation

        if estimated_cost > max_budget:
            validation_result['warnings'].append(f"Budget exceeded: ${estimated_cost:.1f}M > ${max_budget:.1f}M")
            # Changed to warning to allow GA exploration

        # Check deployment bounds
        deployment_plan = configuration.get('deployment_plan', {})
        if 'primary_sector' in deployment_plan:
            coords = deployment_plan['primary_sector'].get('coordinates', [0, 0])
            x, y = coords[0], coords[1]

            deployment_bounds = constraints.get('deployment_bounds', {'min_x': 0, 'max_x': 100, 'min_y': 0, 'max_y': 100})

            if not (deployment_bounds['min_x'] <= x <= deployment_bounds['max_x']):
                validation_result['violations'].append(f"X coordinate out of bounds: {x}")
                validation_result['valid'] = False

            if not (deployment_bounds['min_y'] <= y <= deployment_bounds['max_y']):
                validation_result['violations'].append(f"Y coordinate out of bounds: {y}")
                validation_result['valid'] = False

        # Check task coverage with reasonable constraints
        task_assignments = configuration.get('task_assignments', {})
        total_assigned = sum(assignment.get('assigned_platforms', 0)
                           for assignment in task_assignments.values())

        # Allow some over-allocation (platforms can perform multiple tasks)
        if total_assigned > total_platforms * 1.5:  # Allow 50% over-allocation
            validation_result['warnings'].append(f"High task allocation: {total_assigned} vs {total_platforms} platforms")

        if total_assigned == 0:
            validation_result['violations'].append("No platforms assigned to tasks")
            validation_result['valid'] = False
        elif total_assigned < total_platforms * 0.3:  # At least 30% of platforms should be assigned
            validation_result['warnings'].append(f"Low task allocation: {total_assigned}/{total_platforms} platforms assigned")

    except Exception as e:
        validation_result['valid'] = False
        validation_result['violations'].append(f"Validation error: {e}")

    return validation_result


def fitness_function(ga_instance, solution, solution_idx,
                     indicator_config: Dict[str, Any],
                     fuzzy_config: Dict[str, Any],
                     expert_judgments: str,
                     constraints: Dict[str, Any],
                     gene_config: Dict[str, Any]) -> float:
    """
    Fitness function for genetic algorithm.

    Integrates with AHP-FCE-TOPSIS evaluation pipeline.

    Args:
        ga_instance: PyGAD instance
        solution: Chromosome solution
        solution_idx: Solution index
        indicator_config: Indicator configuration
        fuzzy_config: Fuzzy evaluation configuration
        expert_judgments: Expert judgments file path
        constraints: Constraint specifications
        gene_config: Gene configuration

    Returns:
        Fitness score (Ci value from TOPSIS evaluation)
    """
    try:
        # Decode chromosome to configuration
        configuration = decode_chromosome(solution, gene_config)

        # Validate constraints
        constraint_result = validate_constraints(configuration, constraints)

        if not constraint_result['valid']:
            # Return very low fitness for invalid solutions
            return 0.001

        # Evaluate configuration using AHP-FCE-TOPSIS
        evaluation_result = evaluate_single_scheme(
            configuration, indicator_config, fuzzy_config, expert_judgments
        )

        # Extract Ci score as fitness value
        fitness = evaluation_result.get('ci_score', 0.0)

        # Apply penalty for constraint warnings (soft constraints)
        penalty = 0.0
        for warning in constraint_result.get('warnings', []):
            penalty += 0.1  # Small penalty for each warning

        fitness = max(0.001, fitness - penalty)  # Ensure minimum fitness

        return fitness

    except Exception as e:
        # Return very low fitness for failed evaluations
        print(f"Warning: Fitness function failed for solution {solution_idx}: {e}")
        return 0.001


def calculate_population_diversity(population: np.ndarray) -> float:
    """
    Calculate population diversity metric using Hamming distance.

    Args:
        population: Array of chromosome solutions

    Returns:
        Diversity metric (0-1, higher = more diverse)
    """
    if len(population) < 2:
        return 1.0

    try:
        # Calculate average Hamming distance between all pairs
        total_distance = 0.0
        pair_count = 0

        for i in range(len(population)):
            for j in range(i + 1, len(population)):
                # Hamming distance for integer genes
                distance = np.sum(population[i] != population[j])
                total_distance += distance
                pair_count += 1

        if pair_count == 0:
            return 1.0

        # Normalize by maximum possible distance
        max_distance = population.shape[1]  # Maximum Hamming distance
        avg_distance = total_distance / pair_count
        diversity = avg_distance / max_distance

        return min(1.0, max(0.0, diversity))

    except Exception:
        return 0.0


def optimize_configuration(scenario_config: Dict[str, Any],
                         ga_params: Dict[str, Any],
                         constraints: Dict[str, Any],
                         indicator_config: Dict[str, Any],
                         fuzzy_config: Dict[str, Any],
                         expert_judgments: str) -> Dict[str, Any]:
    """
    Run genetic algorithm optimization for configuration.

    Args:
        scenario_config: Scenario configuration
        ga_params: Genetic algorithm parameters
        constraints: Constraint specifications
        indicator_config: Indicator configuration
        fuzzy_config: Fuzzy evaluation configuration
        expert_judgments: Expert judgments file path

    Returns:
        Dictionary with optimization results
    """
    try:
        print(f"Starting GA optimization for scenario: {scenario_config.get('scenario_id', 'unknown')}")
        print(f"Population size: {ga_params['population_size']}")
        print(f"Generations: {ga_params['num_generations']}")

        # Setup gene configuration based on scenario
        chromosome_config = scenario_config.get('chromosome_encoding', {})
        gene_definitions = chromosome_config.get('genes', [])

        # Extract platform types from scenario
        platform_types = []
        platform_ranges = []

        for gene in gene_definitions:
            if 'usv' in gene['name'].lower() or 'uuv' in gene['name'].lower():
                # Convert gene name to platform type
                platform_name = gene['name'].replace('num_', '').upper()
                if 'usv' in gene['name'].lower():
                    platform_type = f"{platform_name}_Unmanned_Surface_Vessel"
                else:
                    platform_type = f"{platform_name}_Unmanned_Underwater_Vessel"

                platform_types.append(platform_type)
                platform_ranges.append({'low': gene['range'][0], 'high': gene['range'][1] + 1})  # +1 for inclusive range

        gene_config = {
            'platform_types': platform_types,
            'num_deployment_zones': 1,
            'deployment_radius': 50,
            'task_types': ['surveillance', 'anti_submarine', 'mine_countermeasures']
        }

        # Define gene space based on scenario configuration
        num_platform_types = len(platform_types)
        num_deployment_genes = 2  # x, y coordinates
        num_task_genes = 3  # tasks

        gene_space = platform_ranges + [  # Platform counts from scenario
            {'low': 20, 'high': 80} for _ in range(num_deployment_genes)   # Coordinates
        ] + [
            {'low': 1, 'high': 20} for _ in range(num_task_genes)         # Task assignments
        ]

        num_genes = len(gene_space)

        # Track generation history
        generation_history = {
            'best_fitness': [],
            'avg_fitness': [],
            'diversity': [],
            'best_solutions': []
        }

        def on_generation(ga_instance):
            """Callback function called after each generation."""
            generation = ga_instance.generations_completed

            # Calculate fitness statistics
            fitness_scores = ga_instance.last_generation_fitness
            best_fitness = np.max(fitness_scores)
            avg_fitness = np.mean(fitness_scores)

            # Calculate population diversity
            population = ga_instance.population
            diversity = calculate_population_diversity(population)

            # Store history
            generation_history['best_fitness'].append(best_fitness)
            generation_history['avg_fitness'].append(avg_fitness)
            generation_history['diversity'].append(diversity)

            # Store best solution
            best_solution_idx = np.argmax(fitness_scores)
            best_solution = population[best_solution_idx]
            best_fitness_val = fitness_scores[best_solution_idx]

            generation_history['best_solutions'].append({
                'generation': generation,
                'fitness': best_fitness_val,
                'solution': best_solution.tolist(),
                'decoded_config': decode_chromosome(best_solution, gene_config)
            })

            # Display progress
            if generation % 5 == 0 or generation == ga_params['num_generations']:
                print(f"Generation {generation:3d}/{ga_params['num_generations']:3d} | "
                      f"Best Fitness: {best_fitness:.4f} | "
                      f"Avg Fitness: {avg_fitness:.4f} | "
                      f"Diversity: {diversity:.3f}")

        # Create fitness function wrapper
        def fitness_wrapper(ga_instance, solution, solution_idx):
            return fitness_function(
                ga_instance, solution, solution_idx,
                indicator_config, fuzzy_config, expert_judgments,
                constraints, gene_config
            )

        # Initialize PyGAD
        ga_instance = pygad.GA(
            num_generations=ga_params['num_generations'],
            num_parents_mating=ga_params['num_parents_mating'],
            fitness_func=fitness_wrapper,
            sol_per_pop=ga_params['population_size'],
            num_genes=num_genes,
            gene_space=gene_space,
            parent_selection_type=ga_params.get('parent_selection_type', 'tournament'),
            crossover_type=ga_params.get('crossover_type', 'single_point'),
            mutation_type=ga_params.get('mutation_type', 'random'),
            mutation_percent_genes=ga_params.get('mutation_percent_genes', 20),
            keep_parents=ga_params.get('keep_parents', 1),
            random_seed=42,
            on_generation=on_generation
        )

        # Run optimization
        ga_instance.run()

        # Get final results
        best_solution, best_solution_fitness, best_solution_idx = ga_instance.best_solution()

        # Decode best solution
        best_configuration = decode_chromosome(best_solution, gene_config)

        # Evaluate final configuration
        final_evaluation = evaluate_single_scheme(
            best_configuration, indicator_config, fuzzy_config, expert_judgments
        )

        # Prepare results
        results = {
            'optimization_id': f"ga_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'scenario_id': scenario_config.get('scenario_id'),
            'best_configuration': best_configuration,
            'best_fitness': float(best_solution_fitness),
            'final_evaluation': final_evaluation,
            'generation_history': generation_history,
            'ga_parameters': ga_params,
            'constraints': constraints,
            'convergence_info': {
                'total_generations': ga_instance.generations_completed,
                'converged': generation_history['best_fitness'][-1] >= ga_params.get('target_fitness', 0.8) if generation_history['best_fitness'] else False,
                'monotonic_improvement': _check_monotonic_improvement(generation_history['best_fitness']) if generation_history['best_fitness'] else False,
                'final_diversity': generation_history['diversity'][-1] if generation_history['diversity'] else 0.0
            }
        }

        print(f"\nOptimization completed!")
        print(f"Best fitness: {best_solution_fitness:.4f}")
        print(f"Total generations: {ga_instance.generations_completed}")
        print(f"Final diversity: {generation_history['diversity'][-1]:.3f}")

        return results

    except Exception as e:
        raise GAError(f"GA optimization failed: {e}")


def _check_monotonic_improvement(fitness_history: List[float]) -> bool:
    """Check if fitness shows monotonic improvement."""
    if len(fitness_history) < 2:
        return True

    # Check if fitness generally improves (allow small decreases)
    improvements = 0
    for i in range(1, len(fitness_history)):
        if fitness_history[i] > fitness_history[i-1] * 0.95:  # Allow 5% tolerance
            improvements += 1

    return improvements / (len(fitness_history) - 1) > 0.7  # 70% improvement


def plot_convergence(ga_results: Dict[str, Any], output_path: str) -> None:
    """
    Generate convergence plot for GA optimization results.

    Args:
        ga_results: Results from GA optimization
        output_path: Path to save plot
    """
    try:
        generation_history = ga_results['generation_history']

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


if __name__ == "__main__":
    # Example usage and testing
    print("Testing GA Optimizer Module")
    print("Run optimization via main.py CLI for complete functionality.")