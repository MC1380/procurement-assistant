from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from datetime import datetime, timezone
from typing import Literal


class MessageIntent(str, Enum):
    """Possible intentions behind a user message."""

    NEW_REQUEST = "new_request"
    UPDATE_REQUEST = "update_request"
    ASK_QUESTION = "ask_question"
    OTHER = "other"
    UNCLEAR = "unclear"
    CANCEL_REQUEST = "cancel_request"


class RequestExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: MessageIntent
    category_key: str | None = None
    item_name: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    reason: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)
    ambiguous_fields: list[str] = Field(default_factory=list)

    @field_validator("intent", mode="before")
    @classmethod
    def normalize_intent(cls, value):
        """Normalize LLM intent output before Enum validation."""

        if isinstance(value, str):
            return value.strip().lower()

        return value
        
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
    category_key: str | None = Field(
        default=None,
        json_schema_extra={"display_name" : "Product Category"}
    )

    item_name: str | None = Field(
        default=None,
        json_schema_extra={"display_name" : "Product Name"}
    )

    quantity: int | None = Field(
        default=None,
        gt=0,
        json_schema_extra={"display_name" : "Quantity"}
    )

    reason: str | None = Field(
        default=None,
        json_schema_extra={"display_name" : "Purchace Reason"}
    )

    attributes: dict[str, str] = Field(
        default_factory=dict,
    )


class ConversationStatus(str, Enum):
    COLLECTING_INFORMATION = "collecting_information"
    READY_FOR_REVIEW = "ready_for_review"