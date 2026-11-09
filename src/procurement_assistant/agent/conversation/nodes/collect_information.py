"""Node for requesting missing or unclear information."""

from procurement_assistant.agent.conversation.state import ConversationState
from procurement_assistant.database.connection import SessionLocal
from procurement_assistant.services.conversation_response_service import (
    build_information_request_message,
)


def collect_information_node(state: ConversationState) -> dict:
    """Build a response requesting missing or unclear information."""

    request_data = state["request_data"]

    with SessionLocal() as session:
        assistant_message = build_information_request_message(
            category_key=request_data.category_key,
            missing_information=state["missing_information"],
            clarification_fields=state["clarification_fields"],
            session=session,
        )

    return {
        "messages": [assistant_message],
    }