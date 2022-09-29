"""Defines the Factory use cases's requests"""
from dataclasses import dataclass
from cadeia.domain.entities import (
    ProductClasses,
    Factory
)


@ dataclass
class DebitFactoryRequest:
    """Request to debit an Factory when a
        custumer buys something
    """
    factory: Factory
    product_class: ProductClasses
    quantity_of_items: int
    distribution_center: str
