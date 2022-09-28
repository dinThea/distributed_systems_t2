"""Defines the module entities"""
from dataclasses import dataclass
from enum import Enum
from functools import reduce
from typing import Dict, List


class InventoryState(Enum):
    """Defines the state of an CD or Store
    """
    RED = 0
    YELLOW = .25
    GREEN = .50


class ProductClasses(Enum):
    """Defines the accepted classes of an product \
        and its max quantity in a inventory
    """
    A = 100
    B = 60
    C = 20


@dataclass
class Factory:
    """Defines an factory info
    """
    factory_id: str
    produced_classes: List[ProductClasses]


@dataclass
class ProductContainer:
    """Defines the entity of an product container"""
    state: InventoryState
    quantity_of_items: int


@dataclass
class OrderInfo:
    """Defines a container for the order of new products"""
    entity_id: str
    product_class: ProductClasses
    quantity: int


def sum_order_info_quantity(order_list: List[OrderInfo]):
    return reduce(lambda acc, order: acc + order.quantity, order_list, 0)


@dataclass
class Store:
    """Defines the entity of an Store"""
    store_id: str
    warehouses: Dict[ProductClasses, ProductContainer]
    pending_cd_orders: Dict[ProductClasses, List[OrderInfo]]


@dataclass
class DistributionCenter:
    """Defines the entity of an Distribuition Center"""
    distribution_center_id: str
    warehouses: Dict[ProductClasses, ProductContainer]
    pending_store_orders: Dict[ProductClasses, List[OrderInfo]]
    pending_factory_orders: Dict[ProductClasses, List[OrderInfo]]
