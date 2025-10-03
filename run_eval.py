from eval import Config, run_evaluation
from utils import get_samples


def main() -> None:
    configs = [
        Config(model="gpt-5", reasoning_effort="minimal", num_samples=1),
        Config(model="gpt-5", reasoning_effort="low", num_samples=1),
        Config(model="gpt-5", reasoning_effort="medium", num_samples=1),
        Config(model="gpt-5", reasoning_effort="high", num_samples=1),
        Config(model="o3", reasoning_effort="high", num_samples=1),
        Config(model="gpt-5-nano", reasoning_effort="high", num_samples=1),
        Config(model="o3-mini", reasoning_effort="high", num_samples=1),
    ]
    samples = get_samples()
    for config in configs:
        run_evaluation(config, samples, skip_if_exists=True)
        print(
            f"Evaluation complete for {config.model} ({config.reasoning_effort}). Results saved to results/."
        )


if __name__ == "__main__":
    main()
