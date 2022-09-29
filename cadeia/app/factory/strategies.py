"""Strategies
"""
from abc import ABC, abstractmethod
from cadeia.domain.entities import (
    OrderInfo
)


class FactorySendCreditStrategy(ABC):
    """Interface for the transmition of credit to cds"""
    @abstractmethod
    def send_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        ...
