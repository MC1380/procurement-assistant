import pytest

from procurement_assistant.agent.conversation.router import (
    route_conversation,
)
from procurement_assistant.domain.conversation_models import (
    ConversationStatus,
    MessageIntent,
)


@pytest.mark.parametrize(
    ("intent", "status", "expected_route"),
    [
        (
            MessageIntent.ASK_QUESTION,
            ConversationStatus.READY_FOR_REVIEW,
            "answer_question",
        ),
        (
            MessageIntent.CANCEL_REQUEST,
            ConversationStatus.COLLECTING_INFORMATION,
            "handle_cancellation",
        ),
        (
            MessageIntent.OTHER,
            ConversationStatus.COLLECTING_INFORMATION,
            "handle_unrecognized",
        ),
        (
            MessageIntent.UNCLEAR,
            ConversationStatus.READY_FOR_REVIEW,
            "handle_unrecognized",
        ),
        (
            MessageIntent.UPDATE_REQUEST,
            ConversationStatus.COLLECTING_INFORMATION,
            "collect_information",
        ),
        (
            MessageIntent.NEW_REQUEST,
            ConversationStatus.READY_FOR_REVIEW,
            "handoff_to_procurement",
        ),
    ],
)
def test_route_conversation_selects_correct_route(
    intent,
    status,
    expected_route,
):
    """Test routing for different intent and status combinations."""

    state = {
        "last_intent": intent,
        "status": status,
    }

    result = route_conversation(state)

    assert result == expected_route


def test_intent_has_priority_over_status():
    """A question must not trigger procurement handoff."""

    state = {
        "last_intent": MessageIntent.ASK_QUESTION,
        "status": ConversationStatus.READY_FOR_REVIEW,
    }

    result = route_conversation(state)

    assert result == "answer_question"


def test_router_rejects_missing_intent():
    """Routing requires a recognized message intent."""

    state = {
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }

    with pytest.raises(
        ValueError,
        match="Last intent is required for routing.",
    ):
        route_conversation(state)


def test_router_rejects_unsupported_status():
    """Unsupported statuses must not silently select a route."""

    state = {
        "last_intent": MessageIntent.UPDATE_REQUEST,
        "status": "unsupported_status",
    }

    with pytest.raises(
        ValueError,
        match="Unsupported conversation status:",
    ):
        route_conversation(state)