from procurement_assistant.config.llm import get_chat_model
from procurement_assistant.domain.conversation_models import RequestExtraction


def test_llm_connection():
    """Verify that the configured LLM can respond to a request."""

    model = get_chat_model()

    response = model.invoke(
        "Reply with exactly: ProcureFlow AI connection successful."
    )

    assert response.content
    assert isinstance(response.content, str)

    print(f"\nLLM response: {response.content}")


def test_llm_structured_output():
    """Verify that the LLM can extract information into a Pydantic model."""

    model = get_chat_model()

    structured_model = model.with_structured_output(
        RequestExtraction,
        method = "function_calling")

    extraction = structured_model.invoke(
        """
        Extract the procurement request from this message.

        User message: I need 5 industrial pumps.

        Use these rules:
        - intent should be new_request.
        - category_key should be industrial_pump.
        - item_name should identify the requested product.
        - quantity should be 5.
        - Do not invent product attributes that the user did not mention.
        """
    )

    print("\nStructured extraction:")
    print(extraction.model_dump())

    assert isinstance(extraction, RequestExtraction)
    assert extraction.intent.value == "new_request"
    assert extraction.category_key == "industrial_pump"
    assert extraction.quantity == 5