import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


PLOT_CONFIG = {
    "dpi": 300,
    "bbox_inches": "tight",
    "colors": {
        "success": "green",
        "incorrect": "yellow",
        "invalid": "red",
        "missing": "gray",
        "dsl": "#06A77D",
        "naive": "#FF7F50",
        "baseline": "#999999",
    },
    "alpha": {"bar": 0.8, "grid": 0.3, "line": 0.6},
    "fontsize": {"title": 16, "label": 12, "text": 10, "legend": 9},
}


def load_results():
    results_data = {}
    results_dir = Path("results")

    for model_dir in results_dir.iterdir():
        if model_dir.is_dir():
            model_name = model_dir.name.rstrip("__")
            results_data[model_name] = {}

            for result_file in model_dir.glob("*.json"):
                with open(result_file, "r") as f:
                    data = json.load(f)
                graph_name = data["sample"]["name"]
                status = data["status"]
                results_data[model_name][graph_name] = status

    return results_data


def load_detailed_results():
    detailed_results = {}
    results_dir = Path("results")

    for model_dir in results_dir.iterdir():
        if model_dir.is_dir():
            model_name = model_dir.name.rstrip("__")
            detailed_results[model_name] = []

            for result_file in model_dir.glob("*.json"):
                with open(result_file, "r") as f:
                    detailed_results[model_name].append(json.load(f))

    return detailed_results


def calculate_mean_improvement(detailed_results, model_name):
    items = detailed_results.get(model_name, [])
    if not items:
        return float("inf")

    improvements = []
    for r in items:
        naive = r["sample"]["naive_cost"]
        if r["status"] == "Success":
            actual = min(
                r.get("generated_cost", r["sample"]["dsl_cost"]), naive
            )
        else:
            actual = naive
        improvements.append(naive / actual if actual > 0 else 1.0)

    return float(np.mean(improvements))


def add_bar_labels(ax, bars, values, y_offset_factor=0.02, min_offset=0.5, format_str="{:.2f}"):
    for bar, val in zip(bars, values):
        y_offset = max(val * y_offset_factor, min_offset)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + y_offset,
            format_str.format(val),
            ha="center",
            va="bottom",
            fontsize=PLOT_CONFIG["fontsize"]["text"],
        )


def style_bar_plot(ax, title, ylabel, xticklabels, show_grid=True):
    ax.set_ylabel(ylabel, fontsize=PLOT_CONFIG["fontsize"]["label"])
    ax.set_title(title, fontsize=PLOT_CONFIG["fontsize"]["label"])
    ax.set_xticklabels(xticklabels, rotation=45, ha="right")
    if show_grid:
        ax.grid(True, alpha=PLOT_CONFIG["alpha"]["grid"], axis="y")


def create_status_table():
    results = load_results()
    detailed = load_detailed_results()

    all_graphs = sorted(set().union(*[set(r.keys()) for r in results.values()]))
    models = sorted(
        results.keys(), key=lambda m: calculate_mean_improvement(detailed, m)
    )

    df = pd.DataFrame(index=all_graphs, columns=models)
    for model in models:
        for graph in all_graphs:
            df.loc[graph, model] = results[model].get(graph, "Missing")

    status_to_value = {
        "Success": 1,
        "IncorrectReconstruction": 0.5,
        "InvalidDSL": 0,
        "Missing": -1,
    }
    color_df = df.map(lambda x: status_to_value[x])

    fig, ax = plt.subplots(
        figsize=(max(10, len(models) * 2.0), max(12, len(all_graphs) * 0.35))
    )

    cmap = plt.cm.colors.ListedColormap([
        PLOT_CONFIG["colors"]["missing"],
        PLOT_CONFIG["colors"]["invalid"],
        PLOT_CONFIG["colors"]["incorrect"],
        PLOT_CONFIG["colors"]["success"],
    ])
    norm = plt.cm.colors.BoundaryNorm([-1.5, -0.5, 0.25, 0.75, 1.5], cmap.N)

    ax.imshow(color_df.values, cmap=cmap, norm=norm, aspect="auto")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.set_yticks(range(len(all_graphs)))
    ax.set_yticklabels(all_graphs)

    legend_elements = [
        mpatches.Patch(color=PLOT_CONFIG["colors"]["success"], label="Success"),
        mpatches.Patch(color=PLOT_CONFIG["colors"]["incorrect"], label="Incorrect Reconstruction"),
        mpatches.Patch(color=PLOT_CONFIG["colors"]["invalid"], label="Invalid DSL"),
        mpatches.Patch(color=PLOT_CONFIG["colors"]["missing"], label="Missing"),
    ]
    ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))

    ax.set_title("Graph Compression Evaluation Results", fontsize=PLOT_CONFIG["fontsize"]["title"], pad=20)
    ax.set_xlabel("Model", fontsize=PLOT_CONFIG["fontsize"]["label"])
    ax.set_ylabel("Graph", fontsize=PLOT_CONFIG["fontsize"]["label"])

    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_alpha(0.2)

    plt.tight_layout()
    Path("visualization/graph").mkdir(parents=True, exist_ok=True)
    plt.savefig("visualization/graph/results_table.png", **{k: PLOT_CONFIG[k] for k in ["dpi", "bbox_inches"]})
    plt.close()

    print("\nSummary Statistics:")
    for model in models:
        model_results = results[model]
        total = len(model_results)
        success = sum(1 for status in model_results.values() if status == "Success")
        incorrect = sum(1 for status in model_results.values() if status == "IncorrectReconstruction")
        invalid = sum(1 for status in model_results.values() if status == "InvalidDSL")

        print(f"\n{model}:")
        print(f"  Total graphs: {total}")
        print(f"  Success: {success} ({success/total*100:.1f}%)")
        print(f"  Incorrect Reconstruction: {incorrect} ({incorrect/total*100:.1f}%)")
        print(f"  Invalid DSL: {invalid} ({invalid/total*100:.1f}%)")


def create_cost_and_improvement_plot():
    results = load_detailed_results()

    model_names = []
    mean_improvements = []
    median_costs = []
    mean_costs = []
    all_dsl_costs = []
    all_naive_costs = []

    for model_name, model_results in results.items():
        model_names.append(model_name)
        improvements = []
        costs = []

        for r in model_results:
            naive_cost = r["sample"]["naive_cost"]
            dsl_cost = r["sample"]["dsl_cost"]

            if len(all_dsl_costs) < len(model_results):
                all_dsl_costs.append(dsl_cost)
                all_naive_costs.append(naive_cost)

            if r["status"] == "Success":
                actual_cost = min(r.get("generated_cost", dsl_cost), naive_cost)
            else:
                actual_cost = naive_cost

            costs.append(actual_cost)
            improvements.append(naive_cost / actual_cost if actual_cost > 0 else 1.0)

        mean_improvements.append(np.mean(improvements))
        median_costs.append(np.median(costs))
        mean_costs.append(np.mean(costs))

    # Sort by mean improvement
    order = np.argsort(mean_improvements)
    model_names = [model_names[i] for i in order]
    mean_improvements = [mean_improvements[i] for i in order]
    median_costs = [median_costs[i] for i in order]
    mean_costs = [mean_costs[i] for i in order]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(model_names)))

    # Improvement plot
    bars = axes[0].bar(model_names, mean_improvements, alpha=PLOT_CONFIG["alpha"]["bar"], color=colors)
    axes[0].axhline(y=1.0, color=PLOT_CONFIG["colors"]["baseline"], linestyle="--", 
                    alpha=PLOT_CONFIG["alpha"]["line"], label="No improvement (1.0)")
    style_bar_plot(axes[0], "Mean Improvement Over Naive Baseline", "Mean Improvement Ratio", model_names)
    axes[0].legend()
    add_bar_labels(axes[0], bars, mean_improvements)

    # Median cost plot
    median_dsl = np.median(all_dsl_costs)
    median_naive = np.median(all_naive_costs)
    bars = axes[1].bar(model_names, median_costs, alpha=PLOT_CONFIG["alpha"]["bar"], color=colors)
    axes[1].axhline(y=median_dsl, color=PLOT_CONFIG["colors"]["dsl"], linestyle="--",
                    alpha=PLOT_CONFIG["alpha"]["line"], label=f"DSL baseline ({median_dsl:.1f})")
    axes[1].axhline(y=median_naive, color=PLOT_CONFIG["colors"]["naive"], linestyle="--",
                    alpha=PLOT_CONFIG["alpha"]["line"], label=f"Naive baseline ({median_naive:.1f})")
    style_bar_plot(axes[1], "Median Cost Across All Tasks", "Median Cost", model_names)
    axes[1].legend()
    add_bar_labels(axes[1], bars, median_costs, y_offset_factor=0.02, min_offset=max(median_naive * 0.02, 0.5), format_str="{:.1f}")

    # Mean cost plot
    mean_dsl = np.mean(all_dsl_costs)
    mean_naive = np.mean(all_naive_costs)
    bars = axes[2].bar(model_names, mean_costs, alpha=PLOT_CONFIG["alpha"]["bar"], color=colors)
    axes[2].axhline(y=mean_dsl, color=PLOT_CONFIG["colors"]["dsl"], linestyle="--",
                    alpha=PLOT_CONFIG["alpha"]["line"], label=f"DSL baseline ({mean_dsl:.1f})")
    axes[2].axhline(y=mean_naive, color=PLOT_CONFIG["colors"]["naive"], linestyle="--",
                    alpha=PLOT_CONFIG["alpha"]["line"], label=f"Naive baseline ({mean_naive:.1f})")
    style_bar_plot(axes[2], "Mean Cost Across All Tasks", "Mean Cost", model_names)
    axes[2].legend()
    add_bar_labels(axes[2], bars, mean_costs, y_offset_factor=0.02, min_offset=max(mean_naive * 0.02, 0.5), format_str="{:.1f}")

    plt.tight_layout()
    Path("visualization/graph").mkdir(parents=True, exist_ok=True)
    plt.savefig("visualization/graph/cost_and_improvement.png", **{k: PLOT_CONFIG[k] for k in ["dpi", "bbox_inches"]})
    plt.close()


def create_median_dollar_cost_by_model_plot():
    detailed = load_detailed_results()

    price_per_million = {
        "gpt-5": {"in": 1.25, "out": 10.0},
        "gpt-4.1": {"in": 2.0, "out": 8.0},
        "gpt-5-nano": {"in": 0.05, "out": 0.40},
        "o3-pro": {"in": 20.0, "out": 80.00},
    }

    model_names = []
    median_costs = []

    for dir_key, items in detailed.items():
        family = dir_key.split("__")[0]
        if family not in price_per_million:
            continue

        prices = price_per_million[family]
        costs = []
        for r in items:
            usage = r.get("response", {}).get("usage")
            if not usage:
                continue
            prompt_tokens = usage["prompt_tokens"]
            output_tokens = usage.get("total_completion_tokens", 0)
            cost = (prompt_tokens / 1_000_000.0) * prices["in"] + (output_tokens / 1_000_000.0) * prices["out"]
            costs.append(cost)

        if costs:
            model_names.append(dir_key)
            median_costs.append(float(np.median(costs)))

    # Sort by cost
    order = np.argsort(median_costs)
    model_names = [model_names[i] for i in order]
    median_costs = [median_costs[i] for i in order]

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(model_names)))
    bars = ax.bar(model_names, median_costs, color=colors, alpha=PLOT_CONFIG["alpha"]["bar"])
    style_bar_plot(ax, "Median Dollar Cost per Task by Model", "Median $ Cost per Task", model_names)
    add_bar_labels(ax, bars, median_costs, y_offset_factor=0.02, min_offset=0.0005, format_str="${:.4f}")

    plt.tight_layout()
    Path("visualization/graph").mkdir(parents=True, exist_ok=True)
    plt.savefig("visualization/graph/median_dollar_cost_by_model.png", **{k: PLOT_CONFIG[k] for k in ["dpi", "bbox_inches"]})
    plt.close()


if __name__ == "__main__":
    print("Creating status table...")
    create_status_table()

    print("Creating cost and improvement analysis...")
    create_cost_and_improvement_plot()

    print("Creating median $ cost per task by model plot...")
    create_median_dollar_cost_by_model_plot()

    print("\nAll visualizations saved to visualization/graph/")
