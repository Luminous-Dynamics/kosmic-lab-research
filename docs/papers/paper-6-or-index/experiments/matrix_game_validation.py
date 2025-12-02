"""
Matrix Game Validation: Empirical verification of Proposition 2 (Monotonicity under Noise Mixing)

This script validates that O/R Index increases monotonically as we mix noise into a
deterministic policy. Uses a simple 2×2 coordination game to provide intuition.

Expected behavior (Proposition 2):
- Pure deterministic: O/R ≈ -1 (perfect observation-conditioned consistency)
- Partial noise mixing: O/R increases toward 0
- Pure random: O/R = 0 (actions independent of observations)
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import chi2_contingency

# Set random seed for reproducibility
np.random.seed(42)


def compute_or_index_discrete(obs, actions, n_bins=None):
    """
    Compute O/R Index for discrete observations and actions.

    Args:
        obs: (T,) array of discrete observation indices
        actions: (T,) array of discrete action indices
        n_bins: Unused (kept for API compatibility)

    Returns:
        or_index: scalar O/R value
    """
    # Count total action frequencies
    n_actions = int(actions.max()) + 1
    n_obs = int(obs.max()) + 1

    # Compute P(a) - marginal action distribution
    action_counts = np.bincount(actions, minlength=n_actions)
    p_a = action_counts / len(actions)

    # Compute total variance: Var(P(a))
    var_total = np.sum(p_a * (1 - p_a))  # For Bernoulli-like discrete

    # Compute conditional distributions P(a|o) for each observation
    var_conditional = 0.0
    p_o = np.zeros(n_obs)

    for o in range(n_obs):
        mask = (obs == o)
        if np.sum(mask) == 0:
            continue

        p_o[o] = np.sum(mask) / len(obs)

        # P(a|o) for this observation
        actions_given_o = actions[mask]
        action_counts_o = np.bincount(actions_given_o, minlength=n_actions)
        p_a_given_o = action_counts_o / len(actions_given_o)

        # Variance of P(a|o)
        var_o = np.sum(p_a_given_o * (1 - p_a_given_o))
        var_conditional += p_o[o] * var_o

    # Handle edge case: constant actions
    if var_total < 1e-9:
        return -1.0

    or_index = var_conditional / var_total - 1.0
    return or_index


class CoordinationGame:
    """
    2×2 Coordination Game:

    Observation: {0, 1} (e.g., "teammate is LEFT" or "teammate is RIGHT")
    Actions: {0, 1} (e.g., "go LEFT" or "go RIGHT")

    Optimal policy: Match teammate (if obs=0 → action=0, if obs=1 → action=1)
    """

    def __init__(self):
        self.n_obs = 2
        self.n_actions = 2

    def generate_trajectory(self, policy, T=1000):
        """
        Generate trajectory under given policy.

        Args:
            policy: function(obs) → action
            T: trajectory length

        Returns:
            obs: (T,) observation sequence
            actions: (T,) action sequence
        """
        # Observations are uniformly random (50/50 left/right)
        obs = np.random.randint(0, self.n_obs, size=T)

        # Actions determined by policy
        actions = np.array([policy(o) for o in obs])

        return obs, actions


def deterministic_policy(obs):
    """Optimal policy: match observation (coordination)"""
    return obs


def noisy_policy(obs, noise_level):
    """
    Partially noisy policy: mix deterministic with random.

    Args:
        obs: observation
        noise_level: float in [0, 1]
            0 = pure deterministic
            1 = pure random
    """
    # With probability (1-noise_level), follow deterministic policy
    if np.random.rand() > noise_level:
        return obs
    else:
        return np.random.randint(0, 2)


def validate_proposition_2():
    """
    Validate Proposition 2: O/R increases monotonically with noise mixing.

    Test with noise_levels from 0.0 (deterministic) to 1.0 (random).
    Expected: O/R goes from ≈-1 to 0.
    """
    print("="*60)
    print("Validating Proposition 2: Monotonicity under Noise Mixing")
    print("="*60)
    print()

    game = CoordinationGame()
    noise_levels = np.linspace(0.0, 1.0, 11)  # 0, 0.1, ..., 1.0
    or_values = []
    or_stds = []

    T = 10000  # Long trajectory for stable estimates
    n_trials = 10  # Multiple trials for error bars

    print(f"Running {len(noise_levels)} noise levels × {n_trials} trials...")
    print()

    for noise in noise_levels:
        or_trial = []

        for trial in range(n_trials):
            # Generate trajectory with this noise level
            policy = lambda o, n=noise: noisy_policy(o, n)
            obs, actions = game.generate_trajectory(policy, T)

            # Compute O/R
            or_val = compute_or_index_discrete(obs, actions)
            or_trial.append(or_val)

        or_mean = np.mean(or_trial)
        or_std = np.std(or_trial)
        or_values.append(or_mean)
        or_stds.append(or_std)

        print(f"Noise = {noise:.2f}: O/R = {or_mean:+.3f} ± {or_std:.3f}")

    # Check monotonicity
    print()
    print("-"*60)
    print("Monotonicity Check:")
    print("-"*60)

    differences = np.diff(or_values)
    monotonic = np.all(differences >= -1e-6)  # Allow tiny numerical errors

    if monotonic:
        print("✓ O/R increases monotonically with noise level!")
        print(f"  O/R range: [{or_values[0]:.3f}, {or_values[-1]:.3f}]")
        print(f"  Expected for this construction: [-1.0, 0.0]")
        print(f"  (General theory: O/R ∈ [-1, ∞), but noise-mixing stays in [-1, 0])")
    else:
        print("✗ Non-monotonic behavior detected!")
        print(f"  Negative differences: {np.sum(differences < 0)}")

    # Statistical test: Spearman correlation
    from scipy.stats import spearmanr
    rho, p_value = spearmanr(noise_levels, or_values)
    print(f"  Spearman ρ = {rho:.3f} (p = {p_value:.2e})")

    return noise_levels, or_values, or_stds


def plot_proposition_2_validation(noise_levels, or_values, or_stds):
    """Generate publication figure for Proposition 2 validation"""

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot O/R vs noise level with error bars
    ax.errorbar(
        noise_levels, or_values, yerr=or_stds,
        marker='o', markersize=8, linewidth=2, capsize=5,
        color='#2E86AB', label='Empirical O/R',
        alpha=0.8
    )

    # Add theoretical bounds
    ax.axhline(y=-1.0, color='gray', linestyle='--', linewidth=1.5,
               label='Theoretical minimum (deterministic)', alpha=0.7)
    ax.axhline(y=0.0, color='gray', linestyle='--', linewidth=1.5,
               label='Theoretical maximum (random)', alpha=0.7)

    # Styling
    ax.set_xlabel('Noise Level (α)', fontsize=14, fontweight='bold')
    ax.set_ylabel('O/R Index', fontsize=14, fontweight='bold')
    ax.set_title('Proposition 2 Validation: Monotonicity under Noise Mixing',
                 fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.95)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-1.1, 0.3)

    # Add annotation
    ax.annotate(
        'Pure\nDeterministic',
        xy=(0, or_values[0]), xytext=(0.15, -0.8),
        fontsize=10, ha='center',
        arrowprops=dict(arrowstyle='->', color='black', alpha=0.6)
    )
    ax.annotate(
        'Pure\nRandom',
        xy=(1, or_values[-1]), xytext=(0.85, -0.2),
        fontsize=10, ha='center',
        arrowprops=dict(arrowstyle='->', color='black', alpha=0.6)
    )

    plt.tight_layout()

    # Save figure
    output_path = Path("../figures/theory/figure_proposition2_validation.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved figure: {output_path}")

    return fig


def toy_example_for_main_text():
    """
    Generate toy example table for main text (Section 3.5).

    Shows concrete O/R values for 3 policy types in 2×2 coordination game.
    """
    print("\n" + "="*60)
    print("Toy Example: 2×2 Coordination Game")
    print("="*60)
    print()
    print("Game Setup:")
    print("  Observations: {LEFT, RIGHT} (teammate position)")
    print("  Actions: {LEFT, RIGHT} (your move)")
    print("  Optimal: Match teammate (if LEFT → LEFT, if RIGHT → RIGHT)")
    print()

    game = CoordinationGame()
    T = 10000

    policies = {
        'Deterministic (optimal)': lambda o: deterministic_policy(o),
        'Partially noisy (50%)': lambda o: noisy_policy(o, 0.5),
        'Random': lambda o: noisy_policy(o, 1.0),
    }

    print("Policy Performance:")
    print("-"*60)
    print(f"{'Policy':<30} | O/R Index | Interpretation")
    print("-"*60)

    results = []

    for name, policy in policies.items():
        obs, actions = game.generate_trajectory(policy, T)
        or_val = compute_or_index_discrete(obs, actions)

        if or_val < -0.5:
            interp = "Strong coordination"
        elif or_val < -0.1:
            interp = "Moderate coordination"
        else:
            interp = "No coordination"

        print(f"{name:<30} | {or_val:+.3f}    | {interp}")
        results.append((name, or_val, interp))

    print("-"*60)
    print()
    print("Interpretation:")
    print("  O/R ≈ -1: Actions fully determined by observations (perfect coordination)")
    print("  O/R ≈ 0:  Actions independent of observations (random)")
    print()
    print("Range Clarification:")
    print("  This experiment: O/R ∈ [-1, 0] (noise-mixing construction)")
    print("  General theory: O/R ∈ [-1, ∞) (can exceed 0 in skewed settings)")
    print("  Lower bound -1 is tight for deterministic policies")
    print()

    # Generate LaTeX table
    print("="*60)
    print("LaTeX Table for Main Text (Section 3.5)")
    print("="*60)
    print()
    print("\\begin{table}[t]")
    print("\\centering")
    print("\\caption{O/R Index in 2×2 Coordination Game}")
    print("\\label{tab:toy_example}")
    print("\\begin{tabular}{lcc}")
    print("\\toprule")
    print("\\textbf{Policy} & \\textbf{O/R Index} & \\textbf{Interpretation} \\\\")
    print("\\midrule")

    for name, or_val, interp in results:
        print(f"{name} & ${or_val:.2f}$ & {interp} \\\\")

    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table}")
    print()

    return results


def main():
    """Run complete matrix game validation"""

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 11

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  Matrix Game Validation: Proposition 2 (Phase 0)         ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    # 1. Toy example for main text
    toy_example_for_main_text()

    # 2. Validate Proposition 2
    noise_levels, or_values, or_stds = validate_proposition_2()

    # 3. Generate figure
    plot_proposition_2_validation(noise_levels, or_values, or_stds)

    print("\n" + "="*60)
    print("✓ Matrix Game Validation Complete!")
    print("="*60)
    print()
    print("Generated files:")
    print("  - ../figures/theory/figure_proposition2_validation.png")
    print()
    print("Next steps:")
    print("  1. Review O/R values match theoretical predictions")
    print("  2. Copy LaTeX table into Section 3.5")
    print("  3. Reference figure in Appendix B")
    print("  4. Proceed to Phase 1 (Overcooked) after theory merge")
    print()


if __name__ == "__main__":
    main()
