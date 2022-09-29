"""Defines the store controller"""
from logging import Logger
from typing import Union
from cadeia.adapters.solutions import Broker
from cadeia.app.store.requests import CreditStoreRequest, DebitStoreRequest

from cadeia.app.store.use_cases import DebitStoreUseCase, StoreReceiveCreditUseCase
from cadeia.domain.entities import (
    InventoryState,
    OrderInfo,
    ProductClasses,
    ProductContainer,
    Store
)


class StoreController:
    """Controller of the store transactions
    """

    def __init__(
            self,
            store_receive_credit_use_case: StoreReceiveCreditUseCase,
            store_debit_use_case: DebitStoreUseCase,
            broker: Broker,
            store: Union[Store, str],
            logger: Logger
    ):
        self._logger = logger
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

    def _receive_callback(self, order_info: OrderInfo, purpose: str):
        """Callback to be passed to the broker to receive messages

        Args:
            order_info (OrderInfo): Information about the order
        """

        if purpose == "credit":
            self._logger.info(
                f'store {self._store.store_id} received credit of {order_info.product_class.name}:{order_info.quantity}')
            self._store = self._store_receive_credit_use_case.execute(CreditStoreRequest(
                store=self._store,
                product_class=order_info.product_class,
                quantity_of_items=order_info.quantity
            )).store
        else:
            self.buy(product_class=order_info.product_class, quantity=order_info.quantity)

    def buy(self, product_class: ProductClasses, quantity: int) -> bool:
        """Access the debit store use case

        Args:
            product_class (ProductClasses): Class of product to buy
            quantity (int): Quantity of product to receive
        """
        self._logger.info('store %s received buy order of %s:%s', self._store.store_id, product_class.name, quantity)
        res = self._store_debit_use_case.execute(DebitStoreRequest(
            store=self._store,
            product_class=product_class,
            quantity_of_items=quantity
        ))
        self._store = res.store
        self._logger.info(
            'store %s buy order of %s:%s result was %s store has %s items of %s remaining, state is %s',
            self._store.store_id,
            product_class.name,
            str(quantity),
            "success" if res.success else "failure",
            self._store.warehouses[product_class].quantity_of_items,
            product_class.name,
            self._store.warehouses[product_class].state.name
        )
        return res.success

    def start(self):
        self._logger.info("store subscribing to store/%s", self._store.store_id)
        self._broker.start_consuming(f"store/{self._store.store_id}", self._receive_callback)
