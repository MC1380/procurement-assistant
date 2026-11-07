
import operator
from typing import Annotated, NotRequired, TypedDict

from procurement_assistant.domain.conversation_models import (
    ConversationMessage,
    ConversationStatus,
    RequestDraft,
    RequestExtraction,
)


class ConversationState(TypedDict):
    """Conversation state for the procurement assistant."""

    # Unique identifier for the conversation.
    conversation_id: str

    # Conversation history. LangGraph appends new messages using this reducer.
    messages: Annotated[list[ConversationMessage], operator.add]

    # Current purchase request.
    request_data: RequestDraft

    # Information that is still missing from the request.
    missing_information: list[str]

    # Fields that need clarification or confirmation.
    clarification_fields: list[str]

    # Current conversation status.
    status: ConversationStatus

    # Temporary input for the current graph execution.
    current_user_message: NotRequired[str]

    # Structured information extracted by the LLM.
    extraction: NotRequired[RequestExtraction | None]
