"""Strategies
"""
from abc import ABC, abstractmethod
from cadeia.domain.entities import (
    OrderInfo
)


class CDRequestCreditStrategy(ABC):
    """Interface for the transmition of order requests"""
    @abstractmethod
    def request_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        ...


class CDSendCreditStrategy(ABC):
    """Interface for the transmition of credit to stores"""
    @abstractmethod
    def send_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        ...
