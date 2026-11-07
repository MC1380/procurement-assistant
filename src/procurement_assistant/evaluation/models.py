from pydantic import BaseModel, ConfigDict, Field

from procurement_assistant.domain.conversation_models import (
    MessageIntent,
    RequestDraft,
)


class ExpectedExtraction(BaseModel):
    """Expected fields for an extraction evaluation case."""

    model_config = ConfigDict(extra="forbid")

    intent: MessageIntent
    category_key: str | None = None
    item_name: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    attributes: dict[str, str] = Field(default_factory=dict)


class EvaluationCase(BaseModel):
    """A single input and its expected extraction result."""

    model_config = ConfigDict(extra="forbid")

    id: str
    user_message: str
    current_request: RequestDraft | None = None
    expected: ExpectedExtraction