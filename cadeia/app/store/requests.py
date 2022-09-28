"""Defines the store use cases's requests"""
from dataclasses import dataclass
from cadeia.domain.entities import (
    ProductClasses,
    Store
)


@ dataclass
class CreditStoreRequest:
    """Request to credit an store when a
        credit order is fullfilled
    """
    store: Store
    product_class: ProductClasses
    quantity_of_items: int


@ dataclass
class DebitStoreRequest:
    """Request to debit an store when a
        custumer buys something
    """
    store: Store
    product_class: ProductClasses
    quantity_of_items: int
