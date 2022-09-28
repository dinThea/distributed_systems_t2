"""Strategies
"""
from abc import ABC, abstractmethod
from cadeia.domain.entities import (
    OrderInfo
)


class RequestCreditStrategy(ABC):
    """Interface for the transmition of order requests"""
    @abstractmethod
    def request_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        ...
