"""Defines module strategies implementations"""
import json
import paho.mqtt.client as paho

from cadeia.app.cd.strategies import CDRequestCreditStrategy, CDSendCreditStrategy
from cadeia.app.store.strategies import RequestCreditStrategy

from cadeia.domain.entities import (
    OrderInfo
)


class PahoCDRequestCreditStrategy(CDRequestCreditStrategy):
    """Interface for the transmition of order requests"""

    def __init__(self, paho_client: paho.Client) -> None:
        self._client = paho_client

    def request_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        self._client.publish(
            f"factory/{order_info.entity_id}",
            payload=json.dumps({
                "entity_id": order_info.entity_id,
                "product_class": order_info.product_class.name,
                "quantity": order_info.quantity,
                "purpose": "debit"
            })
        )


class PahoCDSendCreditStrategy(CDSendCreditStrategy):
    """Interface for the transmition of credit to stores"""

    def __init__(self, paho_client: paho.Client) -> None:
        self._client = paho_client

    def send_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        self._client.publish(
            f"store/{order_info.entity_id}",
            payload=json.dumps({
                "entity_id": order_info.entity_id,
                "product_class": order_info.product_class.name,
                "quantity": order_info.quantity,
                "purpose": "credit"
            })
        )


class PahoRequestCreditStrategy(RequestCreditStrategy):
    """Interface for the transmition of order requests"""

    def __init__(self, paho_client: paho.Client) -> None:
        self._client = paho_client

    def request_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        self._client.publish(
            f"cd/{order_info.entity_id}",
            payload=json.dumps({
                "entity_id": order_info.entity_id,
                "product_class": order_info.product_class.name,
                "quantity": order_info.quantity,
                "purpose": "debit"
            })
        )
