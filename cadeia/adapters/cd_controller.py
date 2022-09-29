"""Defines the cd controller"""
from logging import Logger
from typing import Union
from cadeia.adapters.solutions import Broker
from cadeia.app.cd.requests import (
    CreditDistributionCenterRequest,
    DebitDistributionCenterRequest
)

from cadeia.app.cd.use_cases import (
    DebitDistributionCenterUseCase,
    DistributionCenterReceiveCreditUseCase
)
from cadeia.domain.entities import (
    DistributionCenter,
    InventoryState,
    OrderInfo,
    ProductClasses,
    ProductContainer
)


class CDController:
    """Controller of the cd transactions
    """

    def __init__(
            self,
            cd_receive_credit_use_case: DistributionCenterReceiveCreditUseCase,
            cd_debit_use_case: DebitDistributionCenterUseCase,
            broker: Broker,
            distribution_center: Union[DistributionCenter, str],
            logger: Logger
    ):
        self._logger = logger
        if isinstance(distribution_center, (str,)):
            self._distribution_center: DistributionCenter = DistributionCenter(
                distribution_center_id=distribution_center,
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
                pending_store_orders={
                    ProductClasses.A: [],
                    ProductClasses.B: [],
                    ProductClasses.C: []
                },
                pending_factory_orders={
                    ProductClasses.A: [],
                    ProductClasses.B: [],
                    ProductClasses.C: []
                }
            )
        else:
            self._distribution_center = distribution_center  # type: ignore
        self._cd_receive_credit_use_case = cd_receive_credit_use_case
        self._cd_debit_use_case = cd_debit_use_case
        self._broker = broker

    def _receive_callback(self, order_info: OrderInfo, purpose: str):
        """Callback to be passed to the broker to receive messages

        Args:
            order_info (OrderInfo): Information about the order
        """
        if purpose == "credit":
            self._receive_credit_callback(order_info)
        else:
            self._receive_debit_request_callback(order_info)

    def _receive_credit_callback(
        self,
        order_info: OrderInfo
    ):
        """Callback to be passed to the broker to receive messages

        Args:
            order_info (OrderInfo): Information about the order
        """

        self._distribution_center = self._cd_receive_credit_use_case.execute(
            CreditDistributionCenterRequest(
                distribution_center=self._distribution_center,
                product_class=order_info.product_class,
                quantity_of_items=order_info.quantity
            )).distribution_center

        self._logger.info(
            'cd %s received credit of %s:%s, now cd has %s items of %s remaining, state is %s',
            self._distribution_center.distribution_center_id,
            order_info.product_class.name,
            str(order_info.quantity),
            self._distribution_center.warehouses[order_info.product_class].quantity_of_items,
            order_info.product_class.name,
            self._distribution_center.warehouses[order_info.product_class].state.name
        )

    def _receive_debit_request_callback(
        self,
        order_info: OrderInfo
    ):
        """Access the debit cd use case

        Args:
            product_class (ProductClasses): Class of product to buy
            quantity (int): Quantity of product to receive
        """

        self._logger.info(
            'cd %s received debit order of %s:%s, cd has %s items of %s remaining, state is %s',
            self._distribution_center.distribution_center_id,
            order_info.product_class.name,
            str(order_info.quantity),
            self._distribution_center.warehouses[order_info.product_class].quantity_of_items,
            order_info.product_class.name,
            self._distribution_center.warehouses[order_info.product_class].state.name
        )
        res = self._cd_debit_use_case.execute(DebitDistributionCenterRequest(
            distribution_center=self._distribution_center,
            product_class=order_info.product_class,
            quantity_of_items=order_info.quantity,
            store_id=order_info.entity_id
        ))
        self._distribution_center = res.distribution_center

    def start(self):
        self._logger.info("cd subscribing to cd/%s", self._distribution_center.distribution_center_id)
        self._broker.start_consuming(
            "cd/#",
            self._receive_callback)
