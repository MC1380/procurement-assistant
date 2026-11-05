import json
from datetime import datetime, timezone
from pathlib import Path


def save_evaluation_report(
    model_name: str,
    summary: dict,
    case_results: list[dict],
    results_dir: Path,
) -> Path:
    """
    Save one evaluation run as a separate JSON report.
    """

    timestamp = datetime.now(timezone.utc)

    run_id = timestamp.strftime("%Y%m%dT%H%M%S%fZ")

    report = {
        "run_id": run_id,
        "model": model_name,
        "timestamp": timestamp.isoformat(),
        "summary": summary,
        "case_results": case_results,
    }

    results_dir.mkdir(parents=True, exist_ok=True)

    safe_model_name = model_name.replace("/", "-")

    report_path = (
        results_dir
        / f"evaluation_{safe_model_name}_{run_id}.json"
    )

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return report_path