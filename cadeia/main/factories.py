"""Defines factories
"""
import json
import os
from typing import Callable
from uuid import uuid4
import paho.mqtt.client as paho
from paho import mqtt
from cadeia.adapters.cd_controller import CDController
from cadeia.adapters.store_controller import StoreController
from cadeia.adapters.strategies import PahoCDRequestCreditStrategy, PahoCDSendCreditStrategy, PahoRequestCreditStrategy
from cadeia.app.cd.use_cases import DebitDistributionCenterUseCase, DistributionCenterReceiveCreditUseCase
from cadeia.app.store.use_cases import DebitStoreUseCase, StoreReceiveCreditUseCase

from cadeia.domain.entities import OrderInfo, ProductClasses


class Broker:
    def __init__(self, client: paho.Client):
        self._client = client

    def process_message(self, callback: Callable):
        def decorated(client, userdata, msg):
            processed_msg = json.loads(msg)
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
        return decorated

    def subscribe(self, topic: str, callback: Callable):
        self._client.on_message = self.process_message(callback)
        self._client.subscribe(topic, qos=1)

    def start(self):
        self._client.loop_forever()


def get_client():
    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(os.getenv("HIVEMQTT_USER"), os.getenv("HIVEMQTT_PASSWD"))
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(os.getenv("HIVEMQTT_HOST"), int(os.getenv("HIVEMQTT_PORT")))

    return client


def get_cd():
    client = get_client()
    return CDController(
        cd_receive_credit_use_case=DistributionCenterReceiveCreditUseCase(
            send_credit_strategy=PahoCDSendCreditStrategy(
                paho_client=client
            )
        ),
        cd_debit_use_case=DebitDistributionCenterUseCase(
            request_credit_strategy=PahoCDRequestCreditStrategy(
                paho_client=client
            ),
            send_credit_strategy=PahoCDSendCreditStrategy(
                paho_client=client
            )
        ),
        broker=Broker(client),
        distribution_center=uuid4()
    )


def get_store():
    client = get_client()
    return StoreController(
        store_receive_credit_use_case=StoreReceiveCreditUseCase(),
        store_debit_use_case=DebitStoreUseCase(
            request_credit_strategy=PahoRequestCreditStrategy(
                paho_client=client
            )
        ),
        broker=Broker(client),
        store=uuid4()
    )
