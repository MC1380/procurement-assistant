from pathlib import Path
from time import perf_counter

from langchain_openai import ChatOpenAI


from procurement_assistant.config.llm import get_llm_settings

from procurement_assistant.evaluation.report_service import (
    save_evaluation_report,
)

from procurement_assistant.evaluation.dataset_service import (
    load_evaluation_dataset,
)
from procurement_assistant.services.llm_extraction_service import (
    extract_request,
)
from procurement_assistant.evaluation.metrics_service import (
    evaluate_extraction,
    aggregate_evaluation_results,
)


def run_evaluation(
    dataset_path: Path,
    model: ChatOpenAI | None = None,
    results_dir : Path = Path("data/evaluation/results"),
    model_name: str | None = None,
) -> tuple[dict, list[dict]]:
    """
    Run LLM extraction on every evaluation case
    and generate an evaluation report.
    """

    cases = load_evaluation_dataset(dataset_path)

    case_results = []
    total_latency = 0.0

    for case in cases:
        start_time = perf_counter()

        try:
            actual = extract_request(
                user_message=case.user_message,
                current_request=case.current_request,
                model=model,
            )

        except Exception as exc:
            latency = perf_counter() - start_time
            total_latency += latency

            case_results.append(
                {
                    "case_id": case.id,
                    "structured_output_success": False,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "latency_seconds": round(latency, 3),
                }
            )
            continue

        latency = perf_counter() - start_time
        total_latency += latency

        evaluation = evaluate_extraction(
            expected=case.expected,
            actual=actual,
        )

        case_results.append(
            {
                "case_id": case.id,
                "structured_output_success": True,
                "latency_seconds": round(latency, 3),
                **evaluation,
            }
        )
        
    # Aggregate results after processing all cases.
    successful_results = [
        result
        for result in case_results
        if result["structured_output_success"]
    ]

    if successful_results:
        summary = aggregate_evaluation_results(successful_results)

    else:
      summary = {
            "total_cases": 0,
            "total_fields": 0,
            "correct_fields": 0,
            "field_accuracy": None,
            "intent_accuracy": None,
            "category_accuracy": None,
            "category_total": 0,
        }

    summary["total_cases"] = len(cases)
    summary["successful_extractions"] = len(successful_results)
    summary["failed_extractions"] = len(cases) - len(successful_results)

    summary["structured_output_success_rate"] = (
        len(successful_results) / len(cases)
    )

    summary["average_latency_seconds"] = round(
        total_latency / len(cases),
        3,
    )

    resolved_model_name = (
        model_name
        or getattr(model, "model_name", None)
        or get_llm_settings().model
    )

    save_evaluation_report(
        model_name=resolved_model_name,
        summary=summary,
        case_results=case_results,
        results_dir=results_dir,
    )
    
    return summary, case_results