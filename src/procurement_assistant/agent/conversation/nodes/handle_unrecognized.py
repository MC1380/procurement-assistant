
"""Node for handling unrecognized or unsupported user messages."""

from procurement_assistant.agent.conversation.state import ConversationState
from procurement_assistant.domain.conversation_models import ConversationMessage


def handle_unrecognized_node(_: ConversationState) -> dict:
    """Guide the user when their message is outside the assistant's scope."""

    assistant_message = ConversationMessage(
        role="assistant",
        content=(
            "I'm here to help with industrial procurement. "
            "You can ask about products, create or update a purchase request, "
            "provide missing information, or cancel an existing request. "
            "Could you rephrase your message in that context?"
        ),
    )

    return {
        "messages": [assistant_message],
    }
