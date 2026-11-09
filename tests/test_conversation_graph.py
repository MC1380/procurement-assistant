import pytest
from contextlib import contextmanager

from procurement_assistant.agent.conversation import graph as graph_module
from procurement_assistant.domain.conversation_models import (
    ConversationMessage,
    ConversationStatus,
    MessageIntent,
    RequestDraft,
    RequestExtraction,
)
from procurement_assistant.agent.conversation.nodes import (
    process_message as process_message_module,
)

def test_conversation_graph_processes_user_message(monkeypatch):
    """Test that the graph delegates message processing to the service."""

    fake_session = object()
    captured = {}

    # Simulate the creation and lifecycle of a database session.
    @contextmanager
    def fake_session_local():
        yield fake_session

    # Replace the real database session factory.
    monkeypatch.setattr(
        process_message_module,
        "SessionLocal",
        fake_session_local,
    )

    # Replace the service to isolate the graph node.
    def fake_process_user_message(
        state,
        user_message,
        extraction,
        session,
    ):
        captured["state"] = state
        captured["user_message"] = user_message
        captured["extraction"] = extraction
        captured["session"] = session

        return {
            "messages": [
                ConversationMessage(
                    role="user",
                    content=user_message,
                )
            ],
            "last_intent": extraction.intent,
            "request_data": state["request_data"],
            "missing_information": [],
            "clarification_fields": [],
            "status": ConversationStatus.COLLECTING_INFORMATION,
        }

    monkeypatch.setattr(
        process_message_module,
        "process_user_message",
        fake_process_user_message,
    )

    extraction = RequestExtraction.model_construct(
        intent=MessageIntent.ASK_QUESTION,
    )

    initial_state = {
        "conversation_id": "test-conversation-1",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
        "current_user_message": "What is the price of an industrial pump?",
        "extraction": extraction,
    }

    # Execute the compiled LangGraph workflow.
    result = graph_module.conversation_graph.invoke(initial_state)

    # Verify that the service received the correct dependencies.
    assert captured["user_message"] == initial_state["current_user_message"]
    assert captured["extraction"] is extraction
    assert captured["session"] is fake_session
    assert captured["state"]["conversation_id"] == "test-conversation-1"

    # Verify the graph returned the expected state update.
    assert result["last_intent"] == MessageIntent.ASK_QUESTION
    assert len(result["messages"]) == 1
    assert result["messages"][0].content == initial_state["current_user_message"]


def test_conversation_graph_rejects_missing_user_message(monkeypatch):
    """The graph must reject an empty user message."""

    monkeypatch.setattr(
        process_message_module,
        "SessionLocal",
        lambda: pytest.fail("Session should not be created."),
    )

    initial_state = {
        "conversation_id": "test-conversation-2",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
        "current_user_message": "",
        "extraction": RequestExtraction.model_construct(
            intent=MessageIntent.ASK_QUESTION,
        ),
    }

    with pytest.raises(
        ValueError,
        match="Current user message is required.",
    ):
        graph_module.conversation_graph.invoke(initial_state)


def test_conversation_graph_rejects_missing_extraction(monkeypatch):
    """The graph must reject a missing extraction."""

    monkeypatch.setattr(
        process_message_module,
        "SessionLocal",
        lambda: pytest.fail("Session should not be created."),
    )

    initial_state = {
        "conversation_id": "test-conversation-3",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
        "current_user_message": "I need an industrial pump.",
        "extraction": None,
    }

    with pytest.raises(
        ValueError,
        match="Message extraction is required.",
    ):
        graph_module.conversation_graph.invoke(initial_state)

def test_graph_routes_question_to_answer_question(monkeypatch):
    fake_session = object()

    @contextmanager
    def fake_session_local():
        yield fake_session

    monkeypatch.setattr(
        process_message_module,
        "SessionLocal",
        fake_session_local,
    )

    def fake_process_user_message(
        state,
        user_message,
        extraction,
        session,
    ):
        return {
            "messages": [
                ConversationMessage(
                    role="user",
                    content=user_message,
                )
            ],
            "last_intent": extraction.intent,
            "request_data": state["request_data"],
            "missing_information": [],
            "clarification_fields": [],
            "status": ConversationStatus.READY_FOR_REVIEW,
        }

    monkeypatch.setattr(
        process_message_module,
        "process_user_message",
        fake_process_user_message,
    )

    extraction = RequestExtraction.model_construct(
        intent=MessageIntent.ASK_QUESTION,
    )

    initial_state = {
        "conversation_id": "routing-test-1",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
        "current_user_message": "What is the price?",
        "extraction": extraction,
    }

    result = graph_module.conversation_graph.invoke(initial_state)

    assert result["selected_route"] == "answer_question"


def test_graph_prioritizes_question_over_ready_status(monkeypatch):
    fake_session = object()

    @contextmanager
    def fake_session_local():
        yield fake_session

    monkeypatch.setattr(
        process_message_module,
        "SessionLocal",
        fake_session_local,
    )

    def fake_process_user_message(
        state,
        user_message,
        extraction,
        session,
    ):
        return {
            "messages": [
                ConversationMessage(
                    role="user",
                    content=user_message,
                )
            ],
            "last_intent": extraction.intent,
            "request_data": state["request_data"],
            "missing_information": [],
            "clarification_fields": [],
            "status": ConversationStatus.READY_FOR_REVIEW,
        }

    monkeypatch.setattr(
        process_message_module,
        "process_user_message",
        fake_process_user_message,
    )

    extraction = RequestExtraction.model_construct(
        intent=MessageIntent.ASK_QUESTION,
    )

    initial_state = {
        "conversation_id": "routing-test-2",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.READY_FOR_REVIEW,
        "current_user_message": "I have a question before submitting.",
        "extraction": extraction,
    }

    result = graph_module.conversation_graph.invoke(initial_state)

    assert result["selected_route"] == "answer_question"


def test_graph_routes_unrecognized_message_to_handler():
    """The graph should execute the real unrecognized message node."""

    initial_state = {
        "conversation_id": "unrecognized-test-1",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
        "current_user_message": "Tell me a joke.",
        "extraction": RequestExtraction.model_construct(
            intent=MessageIntent.OTHER,
        ),
    }

    result = graph_module.conversation_graph.invoke(initial_state)

    assert len(result["messages"]) == 2

    assert result["messages"][0].role == "user"
    assert result["messages"][0].content == "Tell me a joke."

    assert result["messages"][1].role == "assistant"
    assert result["messages"][1].content == (
        "I'm here to help with industrial procurement. "
        "You can ask about products, create or update a purchase request, "
        "provide missing information, or cancel an existing request. "
        "Could you rephrase your message in that context?"
    )


def test_conversation_graph_handles_cancellation():
    initial_state = {
        "conversation_id": "cancellation-test-1",
        "messages": [],
        "request_data": RequestDraft(
            category_key="industrial_pump",
            item_name="Industrial Pump",
            quantity=5,
            reason="Production",
            attributes={"flow_rate": "100"},
        ),
        "missing_information": ["head"],
        "clarification_fields": ["quantity"],
        "status": ConversationStatus.COLLECTING_INFORMATION,
        "current_user_message": "Cancel my request.",
        "extraction": RequestExtraction.model_construct(
            intent=MessageIntent.CANCEL_REQUEST,
        ),
    }

    result = graph_module.conversation_graph.invoke(initial_state)

    assert result["request_data"] == RequestDraft()
    assert result["missing_information"] == []
    assert result["clarification_fields"] == []
    assert result["status"] == ConversationStatus.COLLECTING_INFORMATION

    assert len(result["messages"]) == 2
    assert result["messages"][0].role == "user"
    assert result["messages"][1].role == "assistant"
    assert "cancelled" in result["messages"][1].content.lower()
