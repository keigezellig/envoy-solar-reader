import json
import logging
import time

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MqttService:
    MAX_RETRIES = 10

    def __init__(self, host: str, port: int, username: str, password: str, mqtt_client: mqtt.Client):
        self._password = password
        self._username = username
        self._retry_number: int = 0
        self._host = host
        self._port = port
        self._mqtt_client: mqtt.Client = mqtt_client

    def setup(self):
        self._connect()

    def _connect(self):
        try:
            logger.info(f"Connecting to broker at {self._host}:{self._port}")
            self._mqtt_client.username_pw_set(username=self._username, password=self._password)
            self._mqtt_client.connect(host=self._host, port=self._port)
            self._mqtt_client.loop_start()
        except ConnectionError:
            logger.warning(
                "Cannot connect to broker. Retry #{n} out of {max}".format(n=self._retry_number, max=self.MAX_RETRIES))
            self._retry_number += 1
            time.sleep(5)  # Wait a bit..
            if self._retry_number < self.MAX_RETRIES:
                self._connect()
            else:
                raise MqttConnectionException('Cannot connect to broker, giving up')

    def publish_message(self, topic: str, json_payload: str):
        logger.info(f"Publishing {json_payload} to {topic}")
        self._mqtt_client.publish(topic=topic, payload=json_payload)


class MqttConnectionException(Exception):
    def __init__(self, msg: str):
        super(msg)
