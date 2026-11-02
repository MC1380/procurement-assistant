from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime, timezone
from typing import Literal


class MessageIntent(str, Enum):
    """Possible intentions behind a user message."""

    NEW_REQUEST = "new_request"
    UPDATE_REQUEST = "update_request"
    ASK_QUESTION = "ask_question"
    OTHER = "other"
    UNCLEAR = "unclear"


class RequestExtraction(BaseModel):
    """
    Structured information extracted from one user message.

    This model represents updates, not the complete conversation state.
    """

    model_config = ConfigDict(extra="forbid")

    intent: MessageIntent

    category_key: str | None = None
    item_name: str | None = None

    quantity: int | None = Field(
        default=None,
        gt=0,
    )

    reason: str | None = None

    # Only explicitly mentioned technical attributes.
    # Values preserve their original units, e.g. "5 kW".
    attributes: dict[str, str] = Field(
        default_factory=dict,
    )

    # Fields the user explicitly wants to correct.
    correction_fields: list[str] = Field(
        default_factory=list,
    )

    # Fields that need clarification.
    ambiguous_fields: list[str] = Field(
        default_factory=list,
    )

class ConversationMessage(BaseModel):
    """A single message exchanged during a conversation."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class RequestDraft(BaseModel):
    """
    A partial purchase request collected during conversation.

    Unlike PurchaseRequest, SKU and other information
    may still be missing at this stage.
    """

    model_config = ConfigDict(extra="forbid")

    sku: str | None = None
    category_key: str | None = None
    item_name: str | None = None

    quantity: int | None = Field(
        default=None,
        gt=0,
    )

    reason: str | None = None

    attributes: dict[str, str] = Field(
        default_factory=dict,
    )


class ConversationStatus(str, Enum):
    COLLECTING_INFORMATION = "collecting_information"
    READY_FOR_REVIEW = "ready_for_review"