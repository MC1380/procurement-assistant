"""Node for processing the latest user message."""

from procurement_assistant.agent.conversation.state import ConversationState
from procurement_assistant.database.connection import SessionLocal
from procurement_assistant.services.conversation_service import (
    process_user_message,
)


def process_message_node(state: ConversationState) -> dict:
    """Process the latest user message using the conversation service."""

    user_message = state.get("current_user_message")
    extraction = state.get("extraction")

    if not user_message:
        raise ValueError("Current user message is required.")

    if extraction is None:
        raise ValueError("Message extraction is required.")

    with SessionLocal() as session:
        result = process_user_message(
            state=state,
            user_message=user_message,
            extraction=extraction,
            session=session,
        )

    return result