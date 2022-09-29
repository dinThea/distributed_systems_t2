"""Defines the module use cases"""
from cadeia.app.factory.requests import (
    DebitFactoryRequest
)
from cadeia.app.factory.responses import DebitFactoryResponse
from cadeia.app.factory.strategies import FactorySendCreditStrategy
from cadeia.domain.entities import OrderInfo


class DebitFactoryUseCase:
    """Use case of an purchase on a factories
    """

    def __init__(
        self,
        send_credit_strategy: FactorySendCreditStrategy
    ):
        self._send_credit_strategy = send_credit_strategy

    def execute(self, request: DebitFactoryRequest) -> DebitFactoryResponse:
        """Executes the use case of buying on a factories

        Args:
            request (DebitFactoryRequest): Request info

        Returns:
            DebitFactoryResponse: Response
        """
        order = OrderInfo(
            entity_id=request.distribution_center,
            product_class=request.product_class,
            quantity=request.quantity_of_items
        )
        self._send_credit_strategy.send_credit(
            order_info=order
        )
        return DebitFactoryResponse(
            factory=request.factory
        )
