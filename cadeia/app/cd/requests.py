"""Defines the DistributionCenter use cases's requests"""
from dataclasses import dataclass
from cadeia.domain.entities import (
    ProductClasses,
    DistributionCenter
)


@ dataclass
class CreditDistributionCenterRequest:
    """Request to credit an CD when a
        credit order is fullfilled
    """
    distribution_center: DistributionCenter
    product_class: ProductClasses
    quantity_of_items: int


@ dataclass
class DebitDistributionCenterRequest:
    """Request to debit an DistributionCenter when a
        custumer buys something
    """
    distribution_center: DistributionCenter
    product_class: ProductClasses
    quantity_of_items: int
    store_id: str
