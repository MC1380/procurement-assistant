from pathlib import Path

from procurement_assistant.evaluation.runner import (
    run_evaluation,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "extraction_dataset.jsonl"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "results"
)


def main():
    summary, _ = run_evaluation(
        dataset_path=DATASET_PATH,
        results_dir=RESULTS_DIR,
    )

    print("\nEvaluation Summary")
    print("=" * 40)

    for metric, value in summary.items():
        print(f"{metric}: {value}")


if __name__ == "__main__":
    main()