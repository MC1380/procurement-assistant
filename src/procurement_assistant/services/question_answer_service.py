from sqlalchemy.orm import Session

from procurement_assistant.domain.conversation_models import (
    ConversationMessage,
    RequestDraft,
)
from procurement_assistant.services.inventory_service import (
    get_inventory_item,
    get_inventory_items_by_name,
)


def answer_inventory_question(
    request_data: RequestDraft,
    session: Session,
) -> ConversationMessage:

    if request_data.sku:
        inventory_item = get_inventory_item(
            request_data.sku,
            session,
        )

        if inventory_item is None:
            return ConversationMessage(
                role="assistant",
                content=f"Item with SKU {request_data.sku} was not found."
            )

        return ConversationMessage(
            role="assistant",
            content=(
                f"Product: {inventory_item.name}\n"
                f"SKU: {inventory_item.sku}\n"
                f"Available quantity: {inventory_item.available_quantity}"
            )
        )
    
    if request_data.item_name:
        inventory_items = get_inventory_items_by_name(
            request_data.item_name,
            session
        )
        if not inventory_items:
            return ConversationMessage(
                role = 'assistant',
                content = f'Item with Name {request_data.item_name} was not found'
            )
        
        if len(inventory_items) > 1:
            sku_list = "\n".join(
                f"- {item.sku}"
                for item in inventory_items
            )
            return ConversationMessage(
                role = 'assistant',
                content=(
                f"Multiple products found with name '{request_data.item_name}'.\n"
                f"Please select a SKU:\n{sku_list}"
            )


            )
        return ConversationMessage(
            role = 'assistant',
            content=(
            f"Product: {inventory_items[0].name}\n"
            f"SKU: {inventory_items[0].sku}\n"
            f"Available quantity: {inventory_items[0].available_quantity}"
            )
        )
    return ConversationMessage(
        role = 'assistant',
        content = "Item was not found, Please complete SKU or Name"
    )