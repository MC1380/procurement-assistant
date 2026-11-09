"""LangGraph workflow for handling procurement conversations."""

from langgraph.graph import END, START, StateGraph

from procurement_assistant.agent.conversation.nodes.collect_information import (
    collect_information_node,
)
from procurement_assistant.agent.conversation.nodes.process_message import (
    process_message_node,
)
from procurement_assistant.agent.conversation.router import route_conversation
from procurement_assistant.agent.conversation.state import ConversationState


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

    if route == "collect_information":
        builder.add_node(route, collect_information_node)

    else:
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