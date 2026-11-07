
"""LangGraph workflow for handling procurement conversations."""

from procurement_assistant.agent.conversation_state import ConversationState
from procurement_assistant.agent.conversation_router import (
    route_conversation,
)
from procurement_assistant.database.connection import SessionLocal
from procurement_assistant.services.conversation_service import (
    process_user_message,
)

from langgraph.graph import END, START, StateGraph


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


def create_route_node(route_name: str):
    """Create a temporary node that records the selected route."""

    def route_node(state: ConversationState) -> dict:
        return {"selected_route": route_name}

    return route_node


# Build the conversation workflow.
builder = StateGraph(ConversationState)

builder.add_node("process_message", process_message_node)

routes = [
    "answer_question",
    "handle_cancellation",
    "handle_unrecognized",
    "collect_information",
    "handoff_to_procurement",
]

for route in routes:
    builder.add_node(route, create_route_node(route))
    builder.add_edge(route, END)

builder.add_edge(START, "process_message")

builder.add_conditional_edges(
    "process_message",
    route_conversation,
    {
        route: route for route in routes
    },
)

conversation_graph = builder.compile()
