"""Node for cancelling the current purchase request draft."""

from procurement_assistant.agent.conversation.state import ConversationState
from procurement_assistant.domain.conversation_models import (
    ConversationMessage,
    ConversationStatus,
    RequestDraft,
)


def handle_cancellation_node(_: ConversationState) -> dict:
    """Reset the current purchase request draft."""

    assistant_message = ConversationMessage(
        role="assistant",
        content=(
            "Your current purchase request has been cancelled. "
            "You can start a new request whenever you're ready."
        ),
    )

    return {
        "messages": [assistant_message],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }
