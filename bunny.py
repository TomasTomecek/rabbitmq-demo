"""
TODO:
 * allow receiving messages in threads
 * allow adding callback when message is received
"""
from copy import deepcopy
import json
import logging

import pika


# create logger
logger = logging.getLogger("bunny")
logger.handlers = []
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
handler.setFormatter(formatter)
# add ch to logger
logger.addHandler(handler)


EXCHANGE = "ccs"


class Bunny(object):
    """ message bus wrapper """

    def __init__(self):
        logger.debug("opening connection")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        logger.info("connection is opened")

        self.channel.confirm_delivery()
        self.channel.exchange_declare(exchange=EXCHANGE, type='topic', durable=True)
        logger.info("exchange %s declared", EXCHANGE)

    def register_service(self, name):
        result = self.channel.queue_declare(queue=name, durable=True)
        routing_key = "{0}.#".format(name)
        self.channel.queue_bind(name, EXCHANGE, routing_key=routing_key)
        logger.info("bind created: %s -(%s)-> %s", EXCHANGE, routing_key, name)

    def send(self, data, routing_key):
        encoded_data = json.dumps(data)
        logger.debug("[%s] send %s", routing_key, encoded_data)
        self.channel.publish(EXCHANGE, routing_key, encoded_data,
                             pika.BasicProperties(content_type='application/json',
                                                  delivery_mode=2))

    def receive_stream(self, routing_key, ack=True):
        for method, properties, body in self.channel.consume(
            queue=routing_key,
            no_ack=False
        ):
            redelivered = method.redelivered
            routing_key = method.routing_key
            delivery_tag = method.delivery_tag
            logger.debug("%d [%s] -> %s%s",
                         delivery_tag,
                         routing_key,
                         body,
                         " (redelivered!)" if redelivered else "")
            if ack:
                logger.debug("message %d acked", delivery_tag)
                self.channel.basic_ack(method.delivery_tag)
            yield json.loads(body)

    def close(self):
        self.channel.close()
        self.connection.close()


class UpstreamReleaseMonitoring(object):
    """ messaging for URM """

    SERVICE_NAME = "urm"
    TEMPLATE = {
        "name": None,
        "version": None,
    }

    def __init__(self):
        self.b = Bunny()
        self.b.register_service(self.SERVICE_NAME)

    def new_release(self, package_name, release):
        data = deepcopy(self.TEMPLATE)
        data["name"] = package_name
        data["version"] = release
        self.b.send(data, self.SERVICE_NAME + ".release.new")

    def fetch_releases(self, ack=True):
        return self.b.receive_stream(self.SERVICE_NAME, ack=ack)
