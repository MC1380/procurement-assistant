
"""Routing logic for procurement conversations."""

from typing import Literal

from procurement_assistant.agent.conversation_state import ConversationState
from procurement_assistant.domain.conversation_models import (
    ConversationStatus,
    MessageIntent,
)


ConversationRoute = Literal[
    "answer_question",
    "handle_cancellation",
    "handle_unrecognized",
    "collect_information",
    "handoff_to_procurement",
]


def route_conversation(state: ConversationState) -> ConversationRoute:
    """Select the next conversation route based on intent and status."""

    intent = state.get("last_intent")

    if intent is None:
        raise ValueError("Last intent is required for routing.")

    # Handle non-procurement intents first.
    if intent == MessageIntent.ASK_QUESTION:
        return "answer_question"

    if intent == MessageIntent.CANCEL_REQUEST:
        return "handle_cancellation"

    if intent in (MessageIntent.OTHER, MessageIntent.UNCLEAR):
        return "handle_unrecognized"

    # Route procurement requests based on their completion status.
    status = state["status"]

    if status == ConversationStatus.COLLECTING_INFORMATION:
        return "collect_information"

    if status == ConversationStatus.READY_FOR_REVIEW:
        return "handoff_to_procurement"

    raise ValueError(f"Unsupported conversation status: {status}")
