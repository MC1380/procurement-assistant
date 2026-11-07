from sqlalchemy.orm import Session

from procurement_assistant.agent.conversation_state import ConversationState

from procurement_assistant.domain.conversation_models import RequestExtraction, RequestDraft, ConversationMessage, ConversationStatus, MessageIntent

from procurement_assistant.domain.models import ProductAttribute


from procurement_assistant.services.product_knowledge_service import (
    get_product_attributes,
)


def apply_extraction_update(
    current_data: dict,
    extraction: RequestExtraction,
    confirmed_corrections: set[str] | None = None,
) -> tuple[dict, list[str]]:
    """
    Safely merge extracted information into the current request.

    Returns:
        updated_data: The new request snapshot.
        clarification_fields: Fields that need clarification.
    """

    updated_data = {
        **current_data,
        "attributes":(current_data.get("attributes") or {}).copy(),
    }

    confirmed_corrections = confirmed_corrections or set()

    extraction_data = extraction.model_dump(exclude_unset=True)

    extraction_data.pop("correction_fields", None)
    ambiguous_fields = set(extraction_data.pop("ambiguous_fields", []))

    # These fields are metadata, not request data.
    extraction_data.pop("intent", None)

    clarification_fields = []

    scalar_fields = {
        "category_key",
        "item_name",
        "quantity",
        "reason",
    }

    for field, new_value in extraction_data.items():

        if field == "attributes":
            for attribute, value in new_value.items():

                field_name = f"attributes.{attribute}"

                if field_name in ambiguous_fields or attribute in ambiguous_fields:
                    clarification_fields.append(field_name)
                    continue

                if value is None:
                    continue

                old_value = updated_data["attributes"].get(attribute)

                if old_value is None or old_value == value:
                    updated_data["attributes"][attribute] = value

                elif field_name in confirmed_corrections or attribute in confirmed_corrections:
                    updated_data["attributes"][attribute] = value

                else:
                    clarification_fields.append(field_name)

            continue

        if field not in scalar_fields:
            continue

        if field in ambiguous_fields:
            clarification_fields.append(field)
            continue

        if new_value is None:
            continue

        old_value = updated_data.get(field)

        if old_value is None or old_value == new_value:
            updated_data[field] = new_value

        elif field in confirmed_corrections:
            updated_data[field] = new_value

        else:
            clarification_fields.append(field)

    return updated_data, clarification_fields


def find_missing_information(
    request_data: RequestDraft,
    product_attributes: list[ProductAttribute],
) -> list[str]:
    """
    Find required product attributes that have not been provided.

    The required attributes come from the product knowledge database.
    """

    missing_information = []

    for attribute in product_attributes:

        if not attribute.is_required:
            continue

        value = request_data.attributes.get(
            attribute.attribute_key
        )

        if value is None or not value.strip():
            missing_information.append(
                attribute.attribute_key
            )

    return missing_information


def find_missing_information_from_db(
    request_data: RequestDraft,
    session: Session,
) -> list[str]:
    """
    Retrieve product attributes from the database
    and find the required information missing from the request.
    """

    if not request_data.category_key:
        return ["category_key"]

    product_attributes = get_product_attributes(
        request_data.category_key,
        session,
    )

    if product_attributes is None:
        raise ValueError(
            f"Unknown product category: {request_data.category_key}"
        )

    if not product_attributes:
        raise ValueError(
            f"No product attributes configured for: {request_data.category_key}"
        )

    return find_missing_information(
        request_data,
        product_attributes,
    )

def get_resolved_confirmations(
    extraction: RequestExtraction,
    confirmed_corrections: set[str] | None,
) -> set[str]:
    """
    Return only confirmed fields that have a valid, non-ambiguous
    replacement value in the latest extraction.
    """
    if not confirmed_corrections:
        return set()

    extraction_data = extraction.model_dump(exclude_unset=True)
    ambiguous_fields = set(
        extraction_data.get("ambiguous_fields", [])
    )

    resolved_fields = set()

    scalar_fields = {
        "category_key",
        "item_name",
        "quantity",
        "reason",
    }

    for field in scalar_fields:
        value = extraction_data.get(field)

        if (
            field in confirmed_corrections
            and field in extraction_data
            and value is not None
            and not (isinstance(value, str) and not value.strip())
            and field not in ambiguous_fields
        ):
            resolved_fields.add(field)

    attributes = extraction_data.get("attributes") or {}

    for attribute, value in attributes.items():
        field_name = f"attributes.{attribute}"

        is_confirmed = (
            attribute in confirmed_corrections
            or field_name in confirmed_corrections
        )

        is_ambiguous = (
            attribute in ambiguous_fields
            or field_name in ambiguous_fields
        )

        if is_confirmed and not is_ambiguous and value is not None and value.strip():
            resolved_fields.add(field_name)

    return resolved_fields

def process_user_message(
    state: ConversationState,
    user_message: str,
    extraction: RequestExtraction,
    session: Session,
    confirmed_corrections: set[str] | None = None,
) -> dict:
    """
    Process a new user message and return a partial conversation state update.
    """

     # Step 1: Identify the message intent.
    intent = extraction.intent

    user_message_entry = ConversationMessage(
        role="user",
        content=user_message,
    )

    # Step 2: Handle messages that do not modify purchase data.
    non_request_intents = {
        MessageIntent.ASK_QUESTION,
        MessageIntent.OTHER,
        MessageIntent.UNCLEAR,
        MessageIntent.CANCEL_REQUEST,
    }

    if intent in non_request_intents:
        return {
            "messages": [user_message_entry],
            "last_intent": intent,
            "request_data": state["request_data"],
            "missing_information": state["missing_information"],
            "clarification_fields": state["clarification_fields"],
            "status": state["status"],
        }

    # Step 3: Start fresh when a new request is detected.
    if intent == MessageIntent.NEW_REQUEST:
        current_data = RequestDraft().model_dump()
    else:
        current_data = state["request_data"].model_dump()

    # Step 4: Merge newly extracted information.
    updated_data, new_clarifications = apply_extraction_update(
        current_data=current_data,
        extraction=extraction,
        confirmed_corrections=confirmed_corrections,
    )

    # Step 5: Validate the updated request draft.
    updated_request = RequestDraft.model_validate(updated_data)

    # Step 6: Find missing general and product-specific information.
    missing_basic_information = find_missing_basic_information(
        updated_request
    )

    missing_product_information = find_missing_information_from_db(
        request_data=updated_request,
        session=session,
    )

    missing_information = list(
        dict.fromkeys(
            missing_basic_information + missing_product_information
        )
    )

    # Step 7: Preserve clarifications only for the current request.
    if intent == MessageIntent.NEW_REQUEST:
        clarification_fields = set()
    else:
        clarification_fields = set(state["clarification_fields"])

    clarification_fields.update(new_clarifications)

    resolved_fields = get_resolved_confirmations(
        extraction=extraction,
        confirmed_corrections=confirmed_corrections,
    )

    clarification_fields.difference_update(resolved_fields)

    # Step 8: Determine conversation status.
    if missing_information or clarification_fields:
        status = ConversationStatus.COLLECTING_INFORMATION
    else:
        status = ConversationStatus.READY_FOR_REVIEW

    # Step 9: Return only the changes.
    return {
        "messages": [user_message_entry],
        "last_intent": intent,
        "request_data": updated_request,
        "missing_information": missing_information,
        "clarification_fields": sorted(clarification_fields),
        "status": status,
    }

def find_missing_basic_information(
    request_data: RequestDraft,
) -> list[str]:
    """
    Find missing general information required for a purchase request.

    SKU is intentionally excluded because the system will resolve it later.
    """
    missing_information = []

    if not request_data.category_key:
        missing_information.append("category_key")

    if not request_data.item_name or not request_data.item_name.strip():
        missing_information.append("item_name")

    if request_data.quantity is None:
        missing_information.append("quantity")

    return missing_information