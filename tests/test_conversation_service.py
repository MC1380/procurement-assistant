import pytest

from procurement_assistant.database.connection import Base

from procurement_assistant.database.models import (
    ProductCategoryDB,
    ProductAttributeDB,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from unittest.mock import Mock

from procurement_assistant.conversation_state import ConversationState

from procurement_assistant.domain.models import ProductAttribute
from procurement_assistant.domain.conversation_models import (
    MessageIntent,
    RequestExtraction,
    RequestDraft,
    ConversationStatus,
    ConversationMessage,
)

import procurement_assistant.services.conversation_service as conversation_service


@pytest.fixture
def session():
    test_engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=test_engine)

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    with TestSessionLocal() as test_session:
        yield test_session

    test_engine.dispose()


def test_add_new_information_without_losing_existing_data():
    current_data = {
        "category_key": "industrial_motor",
        "attributes": {"power": "5 kW"},
    }

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=5,
    )

    updated, clarification = conversation_service.apply_extraction_update(
        current_data,
        extraction,
    )

    assert updated["quantity"] == 5
    assert updated["category_key"] == "industrial_motor"
    assert updated["attributes"]["power"] == "5 kW"
    assert clarification == []


def test_conflicting_value_requires_clarification():
    current_data = {"quantity": 3}

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=5,
    )

    updated, clarification = conversation_service.apply_extraction_update(
        current_data,
        extraction,
    )

    assert updated["quantity"] == 3
    assert "quantity" in clarification


def test_confirmed_correction_updates_existing_value():
    current_data = {"quantity": 3}

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=5,
    )

    updated, clarification = conversation_service.apply_extraction_update(
        current_data,
        extraction,
        confirmed_corrections={"quantity"},
    )

    assert updated["quantity"] == 5
    assert clarification == []


def test_conflicting_update_requires_confirmation():
    current_data = {"quantity": 3}

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=5,
    )

    updated, clarification = conversation_service.apply_extraction_update(
        current_data,
        extraction,
    )

    assert updated["quantity"] == 3
    assert "quantity" in clarification


def test_attributes_are_merged_individually():
    current_data = {
        "attributes": {
            "power": "5 kW",
            "voltage": "380 V",
        }
    }

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        attributes={"rpm": "1500"},
    )

    updated, clarification = conversation_service.apply_extraction_update(
        current_data,
        extraction,
    )

    assert updated["attributes"] == {
        "power": "5 kW",
        "voltage": "380 V",
        "rpm": "1500",
    }
    assert clarification == []


def test_ambiguous_field_is_not_updated():
    current_data = {"quantity": 3}

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=5,
        ambiguous_fields=["quantity"],
    )

    updated, clarification = conversation_service.apply_extraction_update(
        current_data,
        extraction,
    )

    assert updated["quantity"] == 3
    assert "quantity" in clarification


def test_none_does_not_clear_existing_value():
    current_data = {"quantity": 3}

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=None,
    )

    updated, clarification = conversation_service.apply_extraction_update(
        current_data,
        extraction,
    )

    assert updated["quantity"] == 3
    assert clarification == []


def test_find_missing_required_attributes():
    request = RequestDraft(
        category_key="industrial_motor",
        quantity=3,
        attributes={
            "power": "5 kW",
        },
    )

    product_attributes = [
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="power",
            display_name="Power",
            description="Motor power",
            is_required=True,
        ),
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="voltage",
            display_name="Voltage",
            description="Motor voltage",
            is_required=True,
        ),
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="rpm",
            display_name="RPM",
            description="Rotational speed",
            is_required=True,
        ),
    ]

    missing = conversation_service.find_missing_information(
        request,
        product_attributes,
    )

    assert missing == ["voltage", "rpm"]


def test_optional_attributes_are_not_required():
    request = RequestDraft(
        attributes={"power": "5 kW"},
    )

    product_attributes = [
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="power",
            display_name="Power",
            description="Motor power",
            is_required=True,
        ),
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="color",
            display_name="Color",
            description="Motor color",
            is_required=False,
        ),
    ]

    missing = conversation_service.find_missing_information(
        request,
        product_attributes,
    )

    assert missing == []


def test_empty_attribute_value_is_missing():
    request = RequestDraft(
        attributes={
            "power": "   ",
        },
    )

    product_attributes = [
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="power",
            display_name="Power",
            description="Motor power",
            is_required=True,
        ),
    ]

    missing = conversation_service.find_missing_information(
        request,
        product_attributes,
    )

    assert missing == ["power"]

def test_find_missing_information_from_db(monkeypatch):
    request = RequestDraft(
        category_key="industrial_motor",
        quantity=3,
        attributes={"power": "5 kW"},
    )

    product_attributes = [
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="power",
            display_name="Power",
            description="Motor power",
            is_required=True,
        ),
        ProductAttribute(
            category_key="industrial_motor",
            attribute_key="voltage",
            display_name="Voltage",
            description="Motor voltage",
            is_required=True,
        ),
    ]

    def mock_get_product_attributes(category_key, session):
        assert category_key == "industrial_motor"
        return product_attributes

    monkeypatch.setattr(
        conversation_service,
        "get_product_attributes",
        mock_get_product_attributes,
    )

    missing = conversation_service.find_missing_information_from_db(
        request,
        Mock(),
    )

    assert missing == ["voltage"]


def test_unknown_category_raises_error(monkeypatch):
    request = RequestDraft(
        category_key="unknown_product",
    )

    monkeypatch.setattr(
        conversation_service,
        "get_product_attributes",
        lambda category_key, session: None,
    )

    with pytest.raises(ValueError, match="Unknown product category"):
        conversation_service.find_missing_information_from_db(
            request,
            Mock(),
        )


def test_missing_category_returns_category_key():
    request = RequestDraft()

    missing = conversation_service.find_missing_information_from_db(
        request,
        Mock(),
    )

    assert missing == ["category_key"]

def test_find_missing_basic_information():
    request = RequestDraft(
        category_key="industrial_pump",
        item_name=None,
        quantity=None,
    )

    result = conversation_service.find_missing_basic_information(request)

    assert result == ["item_name", "quantity"]

def test_find_missing_basic_information_returns_empty_list():
    request = RequestDraft(
        category_key="industrial_pump",
        item_name="Industrial Pump",
        quantity=5,
    )

    result = conversation_service.find_missing_basic_information(request)

    assert result == []

def test_get_resolved_confirmations_for_attribute():
    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        attributes={"head": "30"},
    )

    result = conversation_service.get_resolved_confirmations(
        extraction=extraction,
        confirmed_corrections={"head"},
    )

    assert result == {"attributes.head"}

def test_confirmation_without_new_value_does_not_resolve_field():
    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
    )

    result = conversation_service.get_resolved_confirmations(
        extraction=extraction,
        confirmed_corrections={"head"},
    )

    assert result == set()


def test_process_user_message_with_complete_request(session):
    # Arrange: Prepare product knowledge in the test database.
    session.add(
        ProductCategoryDB(
            category_key="industrial_pump",
            display_name="Industrial Pump",
        )
    )

    session.add_all(
        [
            ProductAttributeDB(
                category_key="industrial_pump",
                attribute_key="flow_rate",
                display_name="Flow Rate",
                is_required=True,
            ),
            ProductAttributeDB(
                category_key="industrial_pump",
                attribute_key="head",
                display_name="Head",
                is_required=True,
            ),
            ProductAttributeDB(
                category_key="industrial_pump",
                attribute_key="fluid_type",
                display_name="Fluid Type",
                is_required=True,
            ),
            ProductAttributeDB(
                category_key="industrial_pump",
                attribute_key="operating_temperature",
                display_name="Operating Temperature",
                is_required=True,
            ),
        ]
    )

    session.flush()

    # Arrange: Prepare the initial conversation state.
    state = {
        "conversation_id": "test-conversation-001",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }

    extraction = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        category_key="industrial_pump",
        item_name="Industrial Pump",
        quantity=5,
        reason="Replacement of damaged pump",
        attributes={
            "flow_rate": "20 L/min",
            "head": "30 m",
            "fluid_type": "Water",
            "operating_temperature": "40 C",
        },
    )

    # Act: Process the user's message.
    result = conversation_service.process_user_message(
        state=state,
        user_message="I need 5 industrial pumps.",
        extraction=extraction,
        session=session,
    )

    # Assert: Verify the result.
    assert result["status"] == ConversationStatus.READY_FOR_REVIEW
    assert result["missing_information"] == []
    assert result["clarification_fields"] == []

    assert result["request_data"].item_name == "Industrial Pump"
    assert result["request_data"].quantity == 5
    assert result["request_data"].attributes["head"] == "30 m"

    assert len(result["messages"]) == 1
    assert result["messages"][0].role == "user"



def test_process_user_message_with_missing_product_attributes(session):
    # Arrange: Register product category and required attributes in the database.
    session.add(
        ProductCategoryDB(
            category_key="industrial_pump",
            display_name="Industrial Pump",
        )
    )

    session.add_all([
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="flow_rate",
            display_name="Flow Rate",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="head",
            display_name="Head",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="fluid_type",
            display_name="Fluid Type",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="operating_temperature",
            display_name="Operating Temperature",
            is_required=True,
        ),
    ])

    session.flush()

    state = {
        "conversation_id": "test-conversation-002",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }

    # LLM extracted only the information that the user said.
    extraction = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        category_key="industrial_pump",
        item_name="Industrial Pump",
        quantity=10,
        attributes={},
    )

    # Act: Process the user's message.
    result = conversation_service.process_user_message(
        state=state,
        user_message="I need 10 industrial pumps.",
        extraction=extraction,
        session=session,
    )

    # Assert: Check the result.
    assert result["status"] == ConversationStatus.COLLECTING_INFORMATION

    assert set(result["missing_information"]) == {
        "flow_rate",
        "head",
        "fluid_type",
        "operating_temperature",
    }

    assert result["request_data"].quantity == 10
    assert result["request_data"].item_name == "Industrial Pump"

def test_process_user_message_with_missing_product_attributes_and_is_required_attribute(session):
    # Arrange: Register product category and required attributes in the database.
    session.add(
        ProductCategoryDB(
            category_key="industrial_pump",
            display_name="Industrial Pump",
        )
    )

    session.add_all([
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="flow_rate",
            display_name="Flow Rate",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="head",
            display_name="Head",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="fluid_type",
            display_name="Fluid Type",
            is_required=False,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="operating_temperature",
            display_name="Operating Temperature",
            is_required=False,
        ),
    ])

    session.flush()

    state = {
        "conversation_id": "test-conversation-003",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }

    extraction = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        category_key="industrial_pump",
        item_name="Industrial Pump",
        quantity=10,
        attributes={},
    )

    result = conversation_service.process_user_message(
        state=state,
        user_message="I need 10 industrial pumps.",
        extraction=extraction,
        session=session,
    )

    assert result["status"] == ConversationStatus.COLLECTING_INFORMATION

    assert set(result["missing_information"]) == {
        "flow_rate",
        "head",
    }


def test_process_user_message_preserves_previous_information(session):
    # Arrange
    session.add(
        ProductCategoryDB(
            category_key="industrial_pump",
            display_name="Industrial Pump",
        )
    )

    session.add_all([
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="flow_rate",
            display_name="Flow Rate",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="head",
            display_name="Head",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="fluid_type",
            display_name="Fluid Type",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="operating_temperature",
            display_name="Operating Temperature",
            is_required=True,
        ),
    ])
    session.flush()

    state = {
        "conversation_id": "test-conversation-003",
        "messages": [],
        "request_data": RequestDraft(),
        "missing_information": [],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }

    # First message
    first_extraction = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        category_key="industrial_pump",
        item_name="Industrial Pump",
        quantity=10,
        attributes={},
    )

    first_result = conversation_service.process_user_message(
        state=state,
        user_message="I need 10 industrial pumps.",
        extraction=first_extraction,
        session=session,
    )

    # Simulate LangGraph state update for the next turn.
    state = {
        **state,
        **first_result,
        "messages": state["messages"] + first_result["messages"],
    }

    # Second message: user provides only the missing head.
    second_extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        attributes={"head": "30 meters"},
    )

    second_result = conversation_service.process_user_message(
        state=state,
        user_message="The required head is 30 meters.",
        extraction=second_extraction,
        session=session,
    )

    # Assert
    assert set(first_result["missing_information"]) == {"flow_rate", "fluid_type", "operating_temperature", "head"}
    assert second_result["request_data"].quantity == 10
    assert second_result["request_data"].attributes["head"] == "30 meters"

    assert set(second_result["missing_information"]) == {
        "flow_rate",
        "fluid_type",
        "operating_temperature",
    }

    assert second_result["status"] == ConversationStatus.COLLECTING_INFORMATION
    assert len(second_result["messages"]) == 1


def test_process_user_message_updates_confirmed_quantity_correction(session):
    # Arrange
    session.add(
        ProductCategoryDB(
            category_key="industrial_pump",
            display_name="Industrial Pump",
        )
    )

    session.add_all([
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="flow_rate",
            display_name="Flow Rate",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="head",
            display_name="Head",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="fluid_type",
            display_name="Fluid Type",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="operating_temperature",
            display_name="Operating Temperature",
            is_required=True,
        ),
    ])
    session.flush()

    state = {
        "conversation_id": "test-conversation-004",
        "messages": [],
        "request_data": RequestDraft(
            category_key="industrial_pump",
            item_name="Industrial Pump",
            quantity=10,
        ),
        "missing_information": [
            "flow_rate",
            "head",
            "fluid_type",
            "operating_temperature",
        ],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=15,
    )

    # Act
    result = conversation_service.process_user_message(
        state=state,
        user_message="Actually, I need 15 pumps.",
        extraction=extraction,
        session=session,
        confirmed_corrections={"quantity"},
    )

    # Assert
    assert result["request_data"].quantity == 15
    assert result["request_data"].category_key == "industrial_pump"
    assert result["request_data"].item_name == "Industrial Pump"
    assert "quantity" not in result["clarification_fields"]
    assert result["status"] == ConversationStatus.COLLECTING_INFORMATION

def test_process_user_message_keeps_old_quantity_without_confirmation(session):
    # Arrange
    session.add(
        ProductCategoryDB(
            category_key="industrial_pump",
            display_name="Industrial Pump",
        )
    )
    session.add_all([
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="flow_rate",
            display_name="Flow Rate",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="head",
            display_name="Head",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="fluid_type",
            display_name="Fluid Type",
            is_required=True,
        ),
        ProductAttributeDB(
            category_key="industrial_pump",
            attribute_key="operating_temperature",
            display_name="Operating Temperature",
            is_required=True,
        ),
    ])
    session.flush()

    state = {
        "conversation_id": "test-conversation-005",
        "messages": [],
        "request_data": RequestDraft(
            category_key="industrial_pump",
            item_name="Industrial Pump",
            quantity=10,
        ),
        "missing_information": [
            "flow_rate",
            "head",
            "fluid_type",
            "operating_temperature",
        ],
        "clarification_fields": [],
        "status": ConversationStatus.COLLECTING_INFORMATION,
    }

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=15,
    )

    # Act
    result = conversation_service.process_user_message(
        state=state,
        user_message="Actually, I need 15 pumps.",
        extraction=extraction,
        session=session,
    )

    # Assert
    assert result["request_data"].quantity == 10
    assert "quantity" in result["clarification_fields"]
    assert result["status"] == ConversationStatus.COLLECTING_INFORMATION