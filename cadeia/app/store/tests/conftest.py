"""Data for store use case tests"""
from unittest.mock import MagicMock
import pytest
from cadeia.app.store.use_cases import (
    DebitStoreUseCase,
    StoreReceiveCreditUseCase
)
from cadeia.domain.entities import (
    InventoryState,
    ProductClasses,
    ProductContainer,
    Store
)


@pytest.fixture
def store_green() -> Store:
    """Store with all its inventory full

    Returns:
        Store: Full store
    """
    return Store(
        store_id='loja_dos_sonhos',
        warehouses={
            ProductClasses.A: ProductContainer(
                state=InventoryState.GREEN,
                quantity_of_items=100
            ),
            ProductClasses.B: ProductContainer(
                state=InventoryState.GREEN,
                quantity_of_items=60
            ),
            ProductClasses.C: ProductContainer(
                state=InventoryState.GREEN,
                quantity_of_items=20
            )
        },
        pending_cd_orders={
            ProductClasses.A: [],
            ProductClasses.B: [],
            ProductClasses.C: []
        }
    )


@pytest.fixture
def store_yellow() -> Store:
    """Store with a little less then half full stock

    Returns:
        Store: Half empty store
    """
    return Store(
        store_id='loja_dos_sonhos',
        warehouses={
            ProductClasses.A: ProductContainer(
                state=InventoryState.YELLOW,
                quantity_of_items=49
            ),
            ProductClasses.B: ProductContainer(
                state=InventoryState.YELLOW,
                quantity_of_items=29
            ),
            ProductClasses.C: ProductContainer(
                state=InventoryState.YELLOW,
                quantity_of_items=9
            )
        },
        pending_cd_orders={
            ProductClasses.A: [],
            ProductClasses.B: [],
            ProductClasses.C: []
        }
    )


@pytest.fixture
def store_red():
    """Store with a little less then a quarter of stock

    Returns:
        Store: Store with less then a quarter of stock
    """
    return Store(
        store_id='loja_dos_sonhos',
        warehouses={
            ProductClasses.A: ProductContainer(
                state=InventoryState.RED,
                quantity_of_items=24
            ),
            ProductClasses.B: ProductContainer(
                state=InventoryState.RED,
                quantity_of_items=14
            ),
            ProductClasses.C: ProductContainer(
                state=InventoryState.RED,
                quantity_of_items=4
            )
        },
        pending_cd_orders={
            ProductClasses.A: [],
            ProductClasses.B: [],
            ProductClasses.C: []
        }
    )


@pytest.fixture
def debit_store_use_case() -> DebitStoreUseCase:
    """Returns an use case to debit an store

    Returns:
        DebitStoreUseCase: Use Case
    """
    return DebitStoreUseCase(
        request_credit_strategy=MagicMock()
    )


@pytest.fixture
def credit_store_use_case() -> StoreReceiveCreditUseCase:
    """Returns the use case to credit an store

    Returns:
        StoreReceiveCreditUseCase: Use Case
    """
    return StoreReceiveCreditUseCase()
