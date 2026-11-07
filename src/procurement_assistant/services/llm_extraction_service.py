from procurement_assistant.config.llm import get_chat_model
from procurement_assistant.domain.conversation_models import RequestExtraction, RequestDraft
from langchain_openai import ChatOpenAI


EXTRACTION_PROMPT = """
You are an information extraction component for ProcureFlow AI.

Your task is to extract procurement request information
from the user's latest message.

You will receive:
1. The latest user message.
2. The current procurement request, if one exists.

Return the information using the provided RequestExtraction schema.

Rules:
- Identify the user's intent based on the latest message and context.
- Use NEW_REQUEST when the user clearly starts a new request.
- Use UPDATE_REQUEST when the user clearly modifies the current request.
- Use ASK_QUESTION when the user asks a question.
- Use UNCLEAR when the intent or relationship to the current request
  cannot be determined confidently.
- Extract only information explicitly provided by the user.
- Do not copy existing values into fields that the user did not mention.
- Do not invent missing information.
- If a field is not mentioned, leave it as None or its default value.
- Extract product attributes into the attributes field.
- Identify genuinely ambiguous fields.
- Treat the extraction as partial information from the latest message,
  not as a complete purchase request.
- Never decide whether a modification is authorized.

Intent classification rules:

    - Each RequestDraft represents exactly one product in the current version.
    - If the user clearly requests a different product as an additional item,
    classify the message as NEW_REQUEST.
    - If the user modifies an existing product request,
    classify the message as UPDATE_REQUEST.
    - If the user changes the product in the existing request,
    classify it as UPDATE_REQUEST.
    - Words such as "also" or "another" can indicate a new request
    when the user introduces a different product.
    - Do not classify every message as UPDATE_REQUEST just because
    a current request exists.

Valid product categories:

- industrial_pump
- industrial_motor
- industrial_bearing

Category rules:
- Always use one of the exact category keys listed above.
- Do not create new category keys.
- Map common product names and synonyms to the closest valid category.
- For example, "electric motor" and "electric motors"
  must map to "industrial_motor".
- If the product cannot be confidently mapped to a valid category,
  return category_key as None.
"""


def extract_request(
    user_message: str,
    current_request: RequestDraft | None = None,
    model: ChatOpenAI | None = None,
) -> RequestExtraction:
    """Extract structured procurement information from a user message."""
    if model is None:
        model = get_chat_model()

    structured_model = model.with_structured_output(
        RequestExtraction,
        method="function_calling",
    )

    current_request_data = (
        current_request.model_dump(exclude_none=True)
        if current_request is not None
        else None
    )

    prompt = f"""
    {EXTRACTION_PROMPT}

    Current request:
    {current_request_data}

    Latest user message:
    {user_message}
    """

    return structured_model.invoke(prompt)