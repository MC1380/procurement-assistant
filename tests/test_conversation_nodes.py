from contextlib import contextmanager

from procurement_assistant.agent.conversation.nodes import (
    collect_information as collect_information_module,
)
from procurement_assistant.domain.conversation_models import (
    ConversationMessage,
    RequestDraft,
)
from procurement_assistant.agent.conversation.nodes import (
    handle_cancellation as handle_cancellation_module,
)
from procurement_assistant.domain.conversation_models import (
    ConversationStatus,
)

def test_collect_information_node_builds_assistant_message(monkeypatch):
    fake_session = object()
    captured = {}

    @contextmanager
    def fake_session_local():
        try:
            yield fake_session
        finally:
            captured["session_closed"] = True

    monkeypatch.setattr(
        collect_information_module,
        "SessionLocal",
        fake_session_local,
    )

    def fake_build_information_request_message(
        category_key,
        missing_information,
        clarification_fields,
        session,
    ):
        captured["category_key"] = category_key
        captured["missing_information"] = missing_information
        captured["clarification_fields"] = clarification_fields
        captured["session"] = session

        return ConversationMessage(
            role="assistant",
            content="Please provide the missing information.",
        )

    monkeypatch.setattr(
        collect_information_module,
        "build_information_request_message",
        fake_build_information_request_message,
    )

    state = {
        "request_data": RequestDraft(category_key="industrial_pump"),
        "missing_information": ["quantity", "flow_rate"],
        "clarification_fields": ["attributes.head"],
    }

    result = collect_information_module.collect_information_node(state)

    assert captured["category_key"] == "industrial_pump"
    assert captured["missing_information"] == ["quantity", "flow_rate"]
    assert captured["clarification_fields"] == ["attributes.head"]
    assert captured["session"] is fake_session
    assert captured["session_closed"] is True

    assert "messages" in result
    assert len(result["messages"]) == 1

    assistant_message = result["messages"][0]

    assert assistant_message.role == "assistant"
    assert assistant_message.content == (
        "Please provide the missing information."
    )


from procurement_assistant.agent.conversation.nodes import (
    handle_unrecognized as handle_unrecognized_module,
)


def test_handle_unrecognized_node_returns_guidance_message():
    state = {}

    result = handle_unrecognized_module.handle_unrecognized_node(state)

    assert "messages" in result
    assert len(result["messages"]) == 1

    assistant_message = result["messages"][0]

    assert assistant_message.role == "assistant"
    assert "industrial procurement" in assistant_message.content
    assert "rephrase your message" in assistant_message.content


def test_handle_cancellation_node_resets_request_draft():
    state = {
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
    }

    result = handle_cancellation_module.handle_cancellation_node(state)

    assert result["request_data"] == RequestDraft()
    assert result["missing_information"] == []
    assert result["clarification_fields"] == []
    assert result["status"] == ConversationStatus.COLLECTING_INFORMATION

    assert len(result["messages"]) == 1
    assert result["messages"][0].role == "assistant"
    assert "cancelled" in result["messages"][0].content
