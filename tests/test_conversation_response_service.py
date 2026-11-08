import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from procurement_assistant.database.connection import Base
from procurement_assistant.database.models import (
    ProductCategoryDB,
    ProductAttributeDB,
)
from procurement_assistant.services.conversation_response_service import (
    build_information_request_message,
    get_general_field_labels,
    get_product_attribute_labels,
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
        test_session.add(
            ProductCategoryDB(
                category_key="industrial_pump",
                display_name="Industrial Pump",
            )
        )

        test_session.add_all(
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
            ]
        )

        test_session.flush()
        yield test_session

    test_engine.dispose()


def test_get_general_field_labels():
    labels = get_general_field_labels()

    assert labels["quantity"] == "Quantity"
    assert labels["item_name"] == "Product Name"


def test_get_product_attribute_labels(session):
    labels = get_product_attribute_labels(
        category_key="industrial_pump",
        session=session,
    )

    assert labels == {
        "flow_rate": "Flow Rate",
        "head": "Head",
    }


def test_build_message_with_general_and_product_fields(session):
    message = build_information_request_message(
        category_key="industrial_pump",
        missing_information=["quantity", "flow_rate"],
        clarification_fields=["attributes.head"],
        session=session,
    )

    assert message.role == "assistant"
    assert message.content == (
        "Please provide the following information: "
        "Quantity, Flow Rate. "
        "Please clarify the following information: Head."
    )


def test_build_message_with_general_fields_only(session):
    message = build_information_request_message(
        category_key=None,
        missing_information=["quantity", "item_name"],
        clarification_fields=[],
        session=session,
    )

    assert message.content == (
        "Please provide the following information: "
        "Quantity, Product Name."
    )


def test_unknown_product_category_raises_error(session):
    with pytest.raises(ValueError, match="Unknown product category"):
        get_product_attribute_labels(
            category_key="unknown_category",
            session=session,
        )


def test_unknown_product_attribute_raises_error(session):
    with pytest.raises(ValueError, match="Unknown field"):
        build_information_request_message(
            category_key="industrial_pump",
            missing_information=["unknown_attribute"],
            clarification_fields=[],
            session=session,
        )


def test_attributes_container_cannot_be_requested(session):
    with pytest.raises(ValueError, match="attributes"):
        build_information_request_message(
            category_key="industrial_pump",
            missing_information=["attributes"],
            clarification_fields=[],
            session=session,
        )


def test_build_message_without_missing_or_unclear_fields(session):
    with pytest.raises(ValueError, match="No missing or unclear information"):
        build_information_request_message(
            category_key="industrial_pump",
            missing_information=[],
            clarification_fields=[],
            session=session,
        )