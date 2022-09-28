
from cadeia.app.store.requests import CreditStoreRequest
from cadeia.app.store.use_cases import StoreReceiveCreditUseCase
from cadeia.domain.entities import (
    InventoryState,
    OrderInfo,
    ProductClasses,
    Store
)


def test_yellow_store_turns_green(
    store_yellow: Store,
    credit_store_use_case: StoreReceiveCreditUseCase
):
    """Tests if after an credit of a half full store, the store turns full

    Args:
        store_yellow (Store): Half full Store
        credit_store_use_case (StoreReceiveCreditUseCase): Credit Use Case
    """
    store_yellow.pending_cd_orders[ProductClasses.A].append(
        OrderInfo(
            store_yellow.store_id,
            product_class=ProductClasses.A,
            quantity=51
        )
    )
    store = credit_store_use_case.execute(CreditStoreRequest(
        store=store_yellow,
        product_class=ProductClasses.A,
        quantity_of_items=51
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 100
    assert store.warehouses[ProductClasses.A].state == InventoryState.GREEN
    assert len(store.pending_cd_orders[ProductClasses.A]) == 0


def test_store_receives_more_items_than_allowed(
    store_green: Store,
    credit_store_use_case: StoreReceiveCreditUseCase
):
    """Tests if after an credit that lets the warehouse with an quantity
        of items greater than a full warehouse, the credit just remains the max

    Args:
        store_green (Store): Full Store
        credit_store_use_case (StoreReceiveCreditUseCase): Credit Use Case
    """
    store_green.pending_cd_orders[ProductClasses.A].append(
        OrderInfo(
            store_green.store_id,
            product_class=ProductClasses.A,
            quantity=1
        )
    )
    store = credit_store_use_case.execute(CreditStoreRequest(
        store=store_green,
        product_class=ProductClasses.A,
        quantity_of_items=1
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 100
    assert store.warehouses[ProductClasses.A].state == InventoryState.GREEN
    assert len(store.pending_cd_orders[ProductClasses.A]) == 0


def test_store_remains_green_and_unchanged_if_receives_nonregistered_order(
    store_red: Store,
    credit_store_use_case: StoreReceiveCreditUseCase
):
    """Tests if after an credit with no register on the store list of credit \
        requests enters, nothing happens

    Args:
        store_red (Store): Full Store
        credit_store_use_case (StoreReceiveCreditUseCase): Credit Use Case
    """
    store_red.pending_cd_orders[ProductClasses.A].append(
        OrderInfo(
            store_red.store_id,
            product_class=ProductClasses.A,
            quantity=96
        )
    )
    store = credit_store_use_case.execute(CreditStoreRequest(
        store=store_red,
        product_class=ProductClasses.A,
        quantity_of_items=96
    )).store
    assert store.warehouses[ProductClasses.A].quantity_of_items == 100
    assert store.warehouses[ProductClasses.A].state == InventoryState.GREEN
    assert len(store.pending_cd_orders[ProductClasses.A]) == 0
