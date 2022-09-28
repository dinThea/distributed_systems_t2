"""Defines the store controller"""
from typing import Union
from cadeia.app.store.requests import CreditStoreRequest, DebitStoreRequest

from cadeia.app.store.use_cases import DebitStoreUseCase, StoreReceiveCreditUseCase
from cadeia.domain.entities import (
    InventoryState,
    OrderInfo,
    ProductClasses,
    ProductContainer,
    Store
)
from cadeia.main.factories import Broker


class StoreController:
    """Controller of the store transactions
    """

    def __init__(
            self,
            store_receive_credit_use_case: StoreReceiveCreditUseCase,
            store_debit_use_case: DebitStoreUseCase,
            broker: Broker,
            store: Union[Store, str] = None
    ):
        if isinstance(store, (str,)):
            self._store: Store = Store(
                store_id=store,
                warehouses={
                    ProductClasses.A: ProductContainer(
                        state=InventoryState.RED,
                        quantity_of_items=0
                    ),
                    ProductClasses.B: ProductContainer(
                        state=InventoryState.RED,
                        quantity_of_items=0
                    ),
                    ProductClasses.C: ProductContainer(
                        state=InventoryState.RED,
                        quantity_of_items=0
                    )
                },
                pending_cd_orders={
                    ProductClasses.A: [],
                    ProductClasses.B: [],
                    ProductClasses.C: []
                }
            )
        else:
            self._store = store  # type: ignore
        self._store_receive_credit_use_case = store_receive_credit_use_case
        self._store_debit_use_case = store_debit_use_case
        self._broker = broker
        self._broker.subscribe(f"store/{store.store_id}", self._receive_callback)  # type: ignore

    def _receive_callback(self, order_info: OrderInfo, _: str):
        """Callback to be passed to the broker to receive messages

        Args:
            order_info (OrderInfo): Information about the order
        """
        self._store = self._store_receive_credit_use_case.execute(CreditStoreRequest(
            store=self._store,
            product_class=order_info.product_class,
            quantity_of_items=order_info.quantity
        )).store

    def buy(self, product_class: ProductClasses, quantity: int) -> bool:
        """Access the debit store use case

        Args:
            product_class (ProductClasses): Class of product to buy
            quantity (int): Quantity of product to receive
        """
        res = self._store_debit_use_case.execute(DebitStoreRequest(
            store=self._store,
            product_class=product_class,
            quantity_of_items=quantity
        ))
        self._store = res.store
        return res.success

    def start(self):
        self._broker.start()
