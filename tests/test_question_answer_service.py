
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from procurement_assistant.database.connection import Base
from procurement_assistant.database.models import InventoryItemDB
from procurement_assistant.domain.conversation_models import RequestDraft
from procurement_assistant.services.question_answer_service import (
    answer_inventory_question,
)


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


def add_inventory_item(
    session,
    sku,
    name,
    available_quantity,
    minimum_quantity=5,
):
    session.add(
        InventoryItemDB(
            sku=sku,
            name=name,
            available_quantity=available_quantity,
            minimum_quantity=minimum_quantity,
        )
    )
    session.commit()


def test_answer_inventory_question_by_existing_sku(session):
    add_inventory_item(
        session,
        sku="MOTOR-001",
        name="Industrial Motor",
        available_quantity=4,
    )

    request_data = RequestDraft(sku="MOTOR-001")

    result = answer_inventory_question(request_data, session)


    assert result.role == "assistant"
    assert "Industrial Motor" in result.content
    assert "MOTOR-001" in result.content
    assert "4" in result.content


def test_answer_inventory_question_by_missing_sku(session):
    request_data = RequestDraft(sku="UNKNOWN-999")

    result = answer_inventory_question(request_data, session)


    assert result.role == "assistant"
    assert "UNKNOWN-999" in result.content
    assert "not found" in result.content.lower()


def test_answer_inventory_question_by_missing_name(session):
    request_data = RequestDraft(item_name="Unknown Motor")

    result = answer_inventory_question(request_data, session)

    assert result.role == "assistant"
    assert "not found" in result.content.lower()


def test_answer_inventory_question_by_unique_name(session):
    add_inventory_item(
        session,
        sku="MOTOR-001",
        name="Industrial Motor",
        available_quantity=4,
    )

    request_data = RequestDraft(item_name="Industrial Motor")

    result = answer_inventory_question(request_data, session)

    assert result.role == "assistant"
    assert "Industrial Motor" in result.content
    assert "MOTOR-001" in result.content
    assert "4" in result.content


def test_answer_inventory_question_by_duplicated_name(session):
    add_inventory_item(
        session,
        sku="MOTOR-001",
        name="Industrial Motor",
        available_quantity=4,
    )
    add_inventory_item(
        session,
        sku="MOTOR-002",
        name="Industrial Motor",
        available_quantity=8,
    )

    request_data = RequestDraft(item_name="Industrial Motor")

    result = answer_inventory_question(request_data, session)

    assert result.role == "assistant"
    assert "MOTOR-001" in result.content
    assert "MOTOR-002" in result.content
    assert "select a SKU" in result.content


def test_answer_inventory_question_without_identifier(session):
    request_data = RequestDraft()

    result = answer_inventory_question(request_data, session)

    assert result.role == "assistant"
    assert "SKU" in result.content
    assert "Name" in result.content

def test_answer_inventory_question_with_zero_quantity(session):
    add_inventory_item(
        session,
        sku="MOTOR-003",
        name="Industrial Motor",
        available_quantity=0,
    )

    request_data = RequestDraft(sku="MOTOR-003")

    result = answer_inventory_question(request_data, session)

    assert result.role == "assistant"
    assert "MOTOR-003" in result.content
    assert "Available quantity: 0" in result.content