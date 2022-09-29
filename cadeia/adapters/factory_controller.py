"""Defines the factory controller"""
from logging import Logger
from cadeia.adapters.solutions import Broker
from cadeia.app.factory.requests import DebitFactoryRequest

from cadeia.app.factory.use_cases import DebitFactoryUseCase
from cadeia.domain.entities import (
    OrderInfo,
    Factory
)


class FactoryController:
    """Controller of the factory transactions
    """

    def __init__(
            self,
            factory_debit_use_case: DebitFactoryUseCase,
            broker: Broker,
            factory: str,
            logger: Logger
    ):
        self._logger = logger
        self._factory: Factory = Factory(
            factory_id=factory
        )
        self._factory_debit_use_case = factory_debit_use_case
        self._broker = broker

    def _receive_callback(self, order_info: OrderInfo, purpose: str):
        """Callback to be passed to the broker to receive messages

        Args:
            order_info (OrderInfo): Information about the order
        """
        self._logger.info(
            f'factory {self._factory.factory_id} received debit order of {order_info.product_class.name}:{order_info.quantity}')

        self._factory = self._factory_debit_use_case.execute(DebitFactoryRequest(
            factory=self._factory,
            distribution_center=order_info.entity_id,
            product_class=order_info.product_class,
            quantity_of_items=order_info.quantity
        )).factory

    def start(self):
        self._logger.info("factory subscribing to factory/#")
        self._broker.start_consuming(
            "factory/#",
            self._receive_callback)
