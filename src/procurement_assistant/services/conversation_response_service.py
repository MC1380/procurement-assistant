"""Build user-facing messages for procurement conversations."""

from sqlalchemy.orm import Session

from procurement_assistant.domain.conversation_models import (
    ConversationMessage,
    RequestDraft,
)
from procurement_assistant.services.product_knowledge_service import (
    get_product_attributes,
)


def get_general_field_labels() -> dict[str, str]:
    """Extract display names of general request fields from RequestDraft."""
    return {
        name: field.json_schema_extra["display_name"]
        for name, field in RequestDraft.model_fields.items()
        if field.json_schema_extra
        and "display_name" in field.json_schema_extra
    }


def get_product_attribute_labels(
    category_key: str,
    session: Session,
) -> dict[str, str]:
    """Retrieve product attribute display names from the database."""
    product_attributes = get_product_attributes(category_key, session)

    if product_attributes is None:
        raise ValueError(f"Unknown product category: {category_key}")

    return {
        attribute.attribute_key: attribute.display_name
        for attribute in product_attributes
    }


def build_information_request_message(
    category_key: str | None,
    missing_information: list[str],
    clarification_fields: list[str],
    session: Session,
) -> ConversationMessage:
    """Build an assistant message requesting missing or unclear information."""

    if not missing_information and not clarification_fields:
        raise ValueError("No missing or unclear information to request.")

    general_labels = get_general_field_labels()

    requested_fields = [
        *missing_information,
        *clarification_fields,
    ]

    product_attribute_keys = {
        field.removeprefix("attributes.")
        for field in requested_fields
        if field not in general_labels
    }

    product_attribute_labels: dict[str, str] = {}

    if product_attribute_keys:
        if not category_key:
            raise ValueError(
                "Product category is required to resolve product attributes."
            )

        product_attribute_labels = get_product_attribute_labels(
            category_key=category_key,
            session=session,
        )

    def resolve_field_label(field_name: str) -> str:
        normalized_name = field_name.removeprefix("attributes.")

        if normalized_name in general_labels:
            return general_labels[normalized_name]

        if normalized_name not in product_attribute_labels:
            raise ValueError(
                f"Unknown field '{field_name}' "
                f"for product category '{category_key}'."
            )

        return product_attribute_labels[normalized_name]

    missing_labels = list(
        dict.fromkeys(
            resolve_field_label(field)
            for field in missing_information
        )
    )

    clarification_labels = list(
        dict.fromkeys(
            resolve_field_label(field)
            for field in clarification_fields
        )
    )

    message_sections = []

    if missing_labels:
        message_sections.append(
            "Please provide the following information: "
            + ", ".join(missing_labels)
            + "."
        )

    if clarification_labels:
        message_sections.append(
            "Please clarify the following information: "
            + ", ".join(clarification_labels)
            + "."
        )

    return ConversationMessage(
        role="assistant",
        content=" ".join(message_sections),
    )
