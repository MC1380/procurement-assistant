import operator

from typing import Annotated, TypedDict

from procurement_assistant.conversation_models import (
    ConversationMessage,
    ConversationStatus,
    RequestDraft,
)


class ConversationState(TypedDict):
    """
    State used by the conversation workflow.

    Stores conversation history and the current request draft.
    """

    conversation_id: str

    # New messages are appended instead of replacing history.
    messages: Annotated[list[ConversationMessage], operator.add]

    # Latest structured snapshot of the user's request.
    request_data: RequestDraft

    # Required information that has not been provided yet.
    missing_information: list[str]

    # Conflicting or ambiguous fields requiring clarification.
    clarification_fields: list[str]

    status: ConversationStatus