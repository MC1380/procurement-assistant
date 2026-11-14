
from sqlalchemy import select
from sqlalchemy.orm import Session

from procurement_assistant.database.models import InventoryItemDB
from procurement_assistant.domain.models import InventoryItem


def get_inventory_item(
    sku: str,
    session: Session,
) -> InventoryItem | None:
    statement = select(InventoryItemDB).where(
        InventoryItemDB.sku == sku
    )

    db_item = session.scalar(statement)

    if db_item is None:
        return None

    return InventoryItem(
        sku=db_item.sku,
        name=db_item.name,
        available_quantity=db_item.available_quantity,
    )


def get_inventory_items_by_name(
    name: str,
    session: Session,
) -> list[InventoryItem]:
    statement = select(InventoryItemDB).where(
        InventoryItemDB.name == name
    )

    db_items = session.scalars(statement).all()

    return [
        InventoryItem(
            sku=item.sku,
            name=item.name,
            available_quantity=item.available_quantity,
        )
        for item in db_items
    ]