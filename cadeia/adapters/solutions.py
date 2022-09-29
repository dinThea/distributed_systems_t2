"""Defines MQTT Solutions
"""
import json
import traceback
from typing import Callable, Optional
import paho.mqtt.client as paho

from cadeia.domain.entities import OrderInfo, ProductClasses


class Broker:
    def __init__(self, client_callback: Callable[[Callable], paho.Client]):
        self._client_callback = client_callback
        self._client = None

    def process_message(self, callback: Callable):
        def decorated(client, userdata, msg):
            try:
                processed_msg = json.loads(msg.payload)
                callback(
                    OrderInfo(
                        entity_id=processed_msg["entity_id"],
                        product_class=ProductClasses.A
                        if processed_msg["product_class"] == "A" else ProductClasses.B
                        if processed_msg["product_class"] == "B" else ProductClasses.C,
                        quantity=processed_msg["quantity"]
                    ),
                    purpose=processed_msg["purpose"]
                )
            except Exception as exc:
                traceback.print_exc()
        return decorated

    def start_consuming(self, topic: str, callback: Callable):
        if not self._client:
            self._client = self._client_callback(self.process_message(callback))
        self._client.subscribe(topic, qos=1)  # type: ignore
        self._client.loop_forever()  # type: ignore
