import json

from procurement_assistant.evaluation.report_service import (
    save_evaluation_report,
)


def test_save_evaluation_report(tmp_path):
    results_dir = tmp_path / "results"

    summary = {
        "total_cases": 2,
        "field_accuracy": 0.85,
    }

    case_results = [
        {
            "case_id": "case_001",
            "structured_output_success": True,
        }
    ]

    report_path = save_evaluation_report(
        model_name="gpt-4o-mini",
        summary=summary,
        case_results=case_results,
        results_dir=results_dir,
    )

    assert report_path.exists()

    with report_path.open(encoding="utf-8") as file:
        report = json.load(file)

    assert report["model"] == "gpt-4o-mini"
    assert report["summary"] == summary
    assert report["case_results"] == case_results
    assert "run_id" in report
    assert "timestamp" in report

def test_save_evaluation_report_creates_separate_files(tmp_path):
    results_dir = tmp_path / "results"

    first_path = save_evaluation_report(
        model_name="gpt-4o-mini",
        summary={"field_accuracy": 0.80},
        case_results=[],
        results_dir=results_dir,
    )

    second_path = save_evaluation_report(
        model_name="gpt-4o-mini",
        summary={"field_accuracy": 0.90},
        case_results=[],
        results_dir=results_dir,
    )

    assert first_path != second_path
    assert first_path.exists()
    assert second_path.exists()

    assert len(list(results_dir.glob("*.json"))) == 2