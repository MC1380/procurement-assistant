# LLM Evaluation

## Objective

Evaluate the information extraction performance
of LLMs used in ProcureFlow AI.

## Evaluation Dataset

Dataset location:

data/evaluation/extraction_dataset.jsonl

The dataset contains representative procurement
conversation scenarios.

## Metrics

| Metric | Description |
|---|---|
| Intent Accuracy | Correct intent predictions / evaluated cases |
| Field Accuracy | Correct fields / evaluated fields |
| Category Accuracy | Correct categories / evaluated categories |
| Structured Output Success Rate | Successful extractions / total cases |
| Average Latency | Total execution time / total cases |

## Evaluation Methodology

1. Load the evaluation dataset.
2. Execute each case independently.
3. Record extraction failures separately.
4. Evaluate fields only for successful extractions.
5. Aggregate successful case results.
6. Calculate average latency across all attempted cases.

## Model Comparison

Results will be added after running the evaluation
with each selected model.

## Limitations

- Token usage and estimated cost are not implemented yet.
- The current dataset is small and should be expanded.
- API and network failures are recorded separately
  from extraction accuracy.