
from cadeia.app.store.requests import DebitStoreRequest
from cadeia.app.store.use_cases import DebitStoreUseCase
from cadeia.domain.entities import (
    InventoryState,
    OrderInfo,
    ProductClasses,
    Store
)


def test_green_store_turns_yellow(
    store_green: Store,
    debit_store_use_case: DebitStoreUseCase
):
    """Tests if after an debit that lets the warehouse with an quantity
        of items less than half of an full warehouse, the state turns yellow.

    Args:
        store_green (Store): Full Store
        debit_store_use_case (DebitStoreUseCase): Debit Use Case
    """
    store = debit_store_use_case.execute(DebitStoreRequest(
        store=store_green,
        product_class=ProductClasses.A,
        quantity_of_items=50
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 50
    assert store.warehouses[ProductClasses.A].state == InventoryState.YELLOW


def test_green_store_receives_request_if_more_items_than_allowed(
    store_green: Store,
    debit_store_use_case: DebitStoreUseCase
):
    """Tests if after an debit that lets the warehouse with an quantity
        of items greater than a full warehouse, the state remains the same \
            and no debit is done.

    Args:
        store_green (Store): Full Store
        debit_store_use_case (DebitStoreUseCase): Debit Use Case
    """
    store = debit_store_use_case.execute(DebitStoreRequest(
        store=store_green,
        product_class=ProductClasses.A,
        quantity_of_items=101
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 100
    assert store.warehouses[ProductClasses.A].state == InventoryState.GREEN


def test_green_store_remains_green(
    store_green: Store,
    debit_store_use_case: DebitStoreUseCase
):
    """Tests if after an debit that lets the warehouse with an quantity
        of items greater than half of an full warehouse, the state remains green.

    Args:
        store_green (Store): Full Store
        debit_store_use_case (DebitStoreUseCase): Debit Use Case
    """
    store = debit_store_use_case.execute(DebitStoreRequest(
        store=store_green,
        product_class=ProductClasses.A,
        quantity_of_items=49
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 51
    assert store.warehouses[ProductClasses.A].state == InventoryState.GREEN


def test_green_store_turns_red(
    store_green: Store,
    debit_store_use_case: DebitStoreUseCase
):
    """Tests if after an debit that lets the warehouse with an quantity
        of items lesser than a quarter of a full warehouse, the state turns red.

    Args:
        store_green (Store): Full Store
        debit_store_use_case (DebitStoreUseCase): Debit Use Case
    """
    store = debit_store_use_case.execute(DebitStoreRequest(
        store=store_green,
        product_class=ProductClasses.A,
        quantity_of_items=75
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 25
    assert store.warehouses[ProductClasses.A].state == InventoryState.RED
    debit_store_use_case._request_credit_strategy.request_credit.assert_called_with(  # type: ignore # pylint: disable=protected-access
        order_info=OrderInfo(
            entity_id=store.store_id,
            product_class=ProductClasses.A,
            quantity=75
        )
    )


def test_green_store_turns_red_considers_awaiting_orders(
    store_green: Store,
    debit_store_use_case: DebitStoreUseCase
):
    """Tests if after an debit that lets the warehouse with an quantity
        of items lesser than a quarter of a full warehouse, the state turns red.

    Args:
        store_green (Store): Full Store
        debit_store_use_case (DebitStoreUseCase): Debit Use Case
    """
    store_green.pending_cd_orders[ProductClasses.A].append(
        OrderInfo(
            store_green.store_id,
            ProductClasses.A,
            quantity=5
        )
    )
    store = debit_store_use_case.execute(DebitStoreRequest(
        store=store_green,
        product_class=ProductClasses.A,
        quantity_of_items=75
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 25
    assert store.warehouses[ProductClasses.A].state == InventoryState.RED
    debit_store_use_case._request_credit_strategy.request_credit.assert_called_with(  # type: ignore # pylint: disable=protected-access
        order_info=OrderInfo(
            entity_id=store.store_id,
            product_class=ProductClasses.A,
            quantity=70
        )
    )
    assert OrderInfo(
        entity_id=store.store_id,
        product_class=ProductClasses.A,
        quantity=70
    ) in store.pending_cd_orders[ProductClasses.A]
