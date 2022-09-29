"""Defines module strategies implementations"""
import json
from logging import Logger
from typing import Any, Callable, Union
import paho.mqtt.client as paho

from cadeia.app.cd.strategies import CDRequestCreditStrategy, CDSendCreditStrategy
from cadeia.app.factory.strategies import FactorySendCreditStrategy
from cadeia.app.store.strategies import RequestCreditStrategy

from cadeia.domain.entities import (
    OrderInfo
)


class PahoCDRequestCreditStrategy(CDRequestCreditStrategy):
    """Interface for the transmition of order requests"""

    def __init__(self, paho_client_callback: Callable[[], paho.Client], logger: Logger) -> None:
        self._client_callback = paho_client_callback
        self._logger = logger
        self._has_started = False
        self._client: Union[paho.Client, None] = None

    def _decorate_publish_message(self, order_info: OrderInfo):
        def decorated(*args, **kwargs):  # pylint: disable=unused-argument
            self._publish(order_info)
        return decorated

    def _publish(self, order_info: OrderInfo):

        self._logger.info("cd is requesting factory to send %s:%s",
                          order_info.product_class.name,
                          order_info.quantity
                          )
        self._client.publish(  # type: ignore
            topic="factory/any_factory",
            payload=json.dumps(
                {
                    "entity_id": order_info.entity_id,
                    "product_class": order_info.product_class.name,
                    "quantity": order_info.quantity,
                    "purpose": "debit"
                })
        )

    def request_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        if not self._client:
            self._client = self._client_callback(  # type: ignore
                connection_callback=self._decorate_publish_message(order_info)
            )
        else:
            self._publish(order_info)
        if self._client and not self._has_started:
            self._client.loop_start()
            self._has_started = True


class PahoCDSendCreditStrategy(CDSendCreditStrategy):
    """Interface for the transmition of credit to stores"""

    def __init__(self, paho_client_callback: Callable[[], paho.Client], logger: Logger) -> None:
        self._client_callback = paho_client_callback
        self._logger = logger
        self._has_started = False
        self._client: Union[None, paho.Client] = None

    def _decorate_publish_message(self, order_info: OrderInfo):
        def decorated(*args, **kwargs):  # pylint: disable=unused-argument
            self._publish(order_info)
        return decorated

    def _publish(self, order_info: OrderInfo):

        self._logger.info("CD is sending store credit of %s:%s",
                          order_info.product_class.name,
                          order_info.quantity
                          )

        self._client.publish(  # type: ignore
            f"store/{order_info.entity_id}",
            payload=json.dumps({
                "entity_id": order_info.entity_id,
                "product_class": order_info.product_class.name,
                "quantity": order_info.quantity,
                "purpose": "credit"
            })
        )

    def send_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        if not self._client:
            self._client = self._client_callback(  # type: ignore
                connection_callback=self._decorate_publish_message(order_info)
            )
        else:
            self._publish(order_info)
        if self._client and not self._has_started:
            self._client.loop_start()
            self._has_started = True


class PahoFactorySendCreditStrategy(FactorySendCreditStrategy):
    """Interface for the transmition of order requests"""

    def __init__(self, paho_client_callback: Callable[[], paho.Client], logger: Logger) -> None:
        self._client_callback = paho_client_callback
        self._logger = logger
        self._has_started = False
        self._client: Union[None, paho.Client] = None

    def _decorate_publish_message(self, order_info: OrderInfo):
        def decorated(*args, **kwargs):  # pylint: disable=unused-argument
            self._publish(order_info)
        return decorated

    def _publish(self, order_info: OrderInfo):

        self._logger.info("factory is sending credit cd of %s:%s",
                          order_info.product_class.name,
                          order_info.quantity
                          )

        self._client.publish(  # type: ignore
            f"cd/{order_info.entity_id}",
            payload=json.dumps({
                "entity_id": order_info.entity_id,
                "product_class": order_info.product_class.name,
                "quantity": order_info.quantity,
                "purpose": "credit"
            })
        )

    def send_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        if not self._client:
            self._client = self._client_callback(  # type: ignore
                connection_callback=self._decorate_publish_message(order_info)
            )
        else:
            self._publish(order_info)
        if self._client and not self._has_started:
            self._client.loop_start()
            self._has_started = True


class PahoRequestCreditStrategy(RequestCreditStrategy):
    """Interface for the transmition of order requests"""

    def __init__(self, paho_client_callback: Callable[[Any], paho.Client], logger: Logger) -> None:
        self._client_callback = paho_client_callback
        self._logger = logger
        self._has_started = False
        self._client: Union[None, paho.Client] = None

    def _decorate_publish_message(self, order_info: OrderInfo):
        def decorated(*args, **kwargs):  # pylint: disable=unused-argument
            self._publish(order_info)
        return decorated

    def _publish(self, order_info: OrderInfo):
        self._logger.info("store is requesting credit to cd of %s:%s",
                          order_info.product_class.name,
                          order_info.quantity
                          )

        self._client.publish(  # type: ignore
            topic="cd/any_cd",
            payload=json.dumps(
                {
                    "entity_id": order_info.entity_id,
                    "product_class": order_info.product_class.name,
                    "quantity": order_info.quantity,
                    "purpose": "debit"
                })
        )

    def request_credit(self, order_info: OrderInfo):
        """Sends the order request to a broker"""
        if not self._client:
            self._client = self._client_callback(  # type: ignore
                connection_callback=self._decorate_publish_message(order_info)
            )
        else:
            self._publish(order_info)
        if self._client and not self._has_started:
            self._client.loop_start()
            self._has_started = True
