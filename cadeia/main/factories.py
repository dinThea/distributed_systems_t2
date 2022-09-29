"""Defines factories
"""
from concurrent.futures import Executor
import json
from logging import FileHandler, Logger, StreamHandler, getLogger, INFO
import os
from random import choice, randint
from time import sleep
from typing import Callable, List
from uuid import uuid4
import concurrent.futures
import paho.mqtt.client as paho
from paho import mqtt
from cadeia.adapters.cd_controller import CDController
from cadeia.adapters.factory_controller import FactoryController
from cadeia.adapters.solutions import Broker
from cadeia.adapters.store_controller import StoreController
from cadeia.adapters.strategies import PahoCDRequestCreditStrategy, PahoCDSendCreditStrategy, PahoFactorySendCreditStrategy, PahoRequestCreditStrategy
from cadeia.app.cd.use_cases import DebitDistributionCenterUseCase, DistributionCenterReceiveCreditUseCase
from cadeia.app.factory.use_cases import DebitFactoryUseCase
from cadeia.app.store.use_cases import DebitStoreUseCase, StoreReceiveCreditUseCase
from cadeia.domain.entities import ProductClasses

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(FileHandler('cadeia_de_abastecimento.log'))
logger.addHandler(StreamHandler())

# setting callbacks for different events to see if it works, print the message etc.


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc, flush=True)

# with this callback you can see if your publish was successful


def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid), flush=True)

# print which topic was subscribed to


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos), flush=True)

# print message, useful for checking if it was successful


def on_message(client, userdata, msg):
    print("msg")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload), flush=True)

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client


def get_client(
    message_callback=on_message,
    connection_callback=on_connect
):
    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = connection_callback
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    print(os.getenv("HIVEMQTT_USER"), os.getenv("HIVEMQTT_PASSWD"),
          os.getenv("HIVEMQTT_HOST"), int(os.getenv("HIVEMQTT_PORT")))
    client.username_pw_set(os.getenv("HIVEMQTT_USER"), os.getenv("HIVEMQTT_PASSWD"))
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(host=os.getenv("HIVEMQTT_HOST"), port=int(os.getenv("HIVEMQTT_PORT")))

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe
    client.on_message = message_callback
    client.on_publish = on_publish
    return client


def get_cd(logger: Logger):
    return CDController(
        cd_receive_credit_use_case=DistributionCenterReceiveCreditUseCase(
            send_credit_strategy=PahoCDSendCreditStrategy(
                paho_client_callback=get_client,
                logger=logger
            )
        ),
        cd_debit_use_case=DebitDistributionCenterUseCase(
            request_credit_strategy=PahoCDRequestCreditStrategy(
                paho_client_callback=get_client,
                logger=logger
            ),
            send_credit_strategy=PahoCDSendCreditStrategy(
                paho_client_callback=get_client,
                logger=logger
            )
        ),
        broker=Broker(get_client),
        distribution_center=str(uuid4()),
        logger=logger
    )


def get_store(logger: Logger):
    return StoreController(
        store_receive_credit_use_case=StoreReceiveCreditUseCase(),
        store_debit_use_case=DebitStoreUseCase(
            request_credit_strategy=PahoRequestCreditStrategy(
                paho_client_callback=get_client,
                logger=logger
            )
        ),
        broker=Broker(get_client),
        store=str(uuid4()),
        logger=logger
    )


def get_factory(logger: Logger):
    return FactoryController(
        factory_debit_use_case=DebitFactoryUseCase(
            send_credit_strategy=PahoFactorySendCreditStrategy(
                paho_client_callback=get_client,
                logger=logger
            )
        ),
        broker=Broker(get_client),
        factory=str(uuid4()),
        logger=logger
    )


def client_consume(created_stores: List[StoreController]):
    client = get_client()
    client.loop_start()
    client_id = str(uuid4())
    while True:
        product_class: ProductClasses = choice(list(ProductClasses))
        quantity = randint(0, product_class.value)
        selected_store = choice(created_stores)._store  # pylint: disable=protected-access
        logger.info('client %s is buying %s:%s from %s', client_id,
                    product_class.name, quantity, selected_store.store_id)
        info = client.publish(
            topic=f"store/{selected_store.store_id}",
            payload=json.dumps({
                "entity_id": selected_store.store_id,
                "product_class": product_class.name,
                "quantity": quantity,
                "purpose": "debit"
            })
        )
        info.wait_for_publish()
        sleep(randint(10, 5000)/1000)


def create_component(
    pool: Executor,
    creation_callback: Callable,
    number: int,
    name: str
):
    components = []
    for i in range(number):
        component = creation_callback()
        job = pool.submit(component.start)
        components.append(component)
        try:
            job.exception(1)
        except concurrent.futures._base.TimeoutError as _:  # pylint: disable=protected-access
            logger.info('running')
        logger.info("created %sst %s", str(i+1), name)
    return components
