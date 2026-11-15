"""Node for answering inventory-related questions."""

from procurement_assistant.agent.conversation.state import ConversationState
from procurement_assistant.database.connection import SessionLocal
from procurement_assistant.services.question_answer_service import (
    answer_inventory_question,
)


def answer_inventory_question_node(state: ConversationState) -> dict:
    """Answer an inventory-related user question."""

    request_data = state["request_data"]

    with SessionLocal() as session:
        assistant_message = answer_inventory_question(
            request_data=request_data,
            session=session,
        )

    return {
        "messages": [assistant_message],
    }
