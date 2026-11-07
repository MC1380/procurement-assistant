from procurement_assistant.domain.conversation_models import RequestExtraction
from procurement_assistant.evaluation_models import ExpectedExtraction


def evaluate_extraction(
    expected: ExpectedExtraction,
    actual: RequestExtraction,
) -> dict:
    """
    Compare an actual LLM extraction with the expected extraction.

    Only explicitly provided expected fields are evaluated.
    """

    expected_data = expected.model_dump(exclude_unset=True)

    field_results = {}

    for field_name, expected_value in expected_data.items():

        # Evaluate product attributes individually.
        if field_name == "attributes":
            for attribute_name, attribute_value in expected_value.items():
                actual_value = actual.attributes.get(attribute_name)

                field_results[f"attributes.{attribute_name}"] = {
                    "expected": attribute_value,
                    "actual": actual_value,
                    "correct": actual_value == attribute_value,
                }

            continue

        actual_value = getattr(actual, field_name)

        # Convert Enum values into strings for readable results.
        if hasattr(expected_value, "value"):
            expected_value = expected_value.value

        if hasattr(actual_value, "value"):
            actual_value = actual_value.value

        field_results[field_name] = {
            "expected": expected_value,
            "actual": actual_value,
            "correct": actual_value == expected_value,
        }

    total_fields = len(field_results)

    correct_fields = sum(
        result["correct"]
        for result in field_results.values()
    )

    field_accuracy = (
        correct_fields / total_fields
        if total_fields > 0
        else 0.0
    )

    return {
        "field_results": field_results,
        "total_fields": total_fields,
        "correct_fields": correct_fields,
        "field_accuracy": field_accuracy,
    }

def aggregate_evaluation_results(
    case_results: list[dict],
) -> dict:
    """
    Aggregate individual case evaluation results
    into a single evaluation report.
    """

    if not case_results:
        raise ValueError("Evaluation results are empty.")

    total_cases = len(case_results)

    total_fields = sum(
        result["total_fields"]
        for result in case_results
    )

    correct_fields = sum(
        result["correct_fields"]
        for result in case_results
    )

    intent_correct = 0
    category_correct = 0
    category_total = 0

    for result in case_results:
        field_results = result["field_results"]

        # Calculate intent accuracy.
        if field_results["intent"]["correct"]:
            intent_correct += 1

        # Calculate category accuracy only
        # for cases where category was evaluated.
        if "category_key" in field_results:
            category_total += 1

            if field_results["category_key"]["correct"]:
                category_correct += 1

    return {
        "total_cases": total_cases,
        "total_fields": total_fields,
        "correct_fields": correct_fields,
        "field_accuracy": correct_fields / total_fields
        if total_fields else 0.0,
        "intent_accuracy": intent_correct / total_cases,
        "category_accuracy": category_correct / category_total
        if category_total else None,
        "category_total": category_total,
    }