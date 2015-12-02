"""
TODO:
 * allow receiving messages in threads
"""
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
        self.channel.exchange_declare(exchange=EXCHANGE, type='topic', durable=True)
        logger.info("exchange %s declared", EXCHANGE)

    def register_service(self, name):
        result = self.channel.queue_declare(durable=True)
        queue_name = result.method.queue
        routing_key = "{0}.#".format(name)
        self.channel.queue_bind(queue_name, EXCHANGE, routing_key=routing_key)
        logger.info("bind created: %s -(%s)-> %s", EXCHANGE, routing_key, queue_name)

    def send(self, text, routing_key):
        self.channel.publish(EXCHANGE, routing_key, text,
                             pika.BasicProperties(content_type='text/plain',
                                                  delivery_mode=1))

    def receive(self, routing_key, callback):
        self.channel.basic_consume(callback,
                              queue='hello',
                              no_ack=False)

        self.channel.start_consuming()

    def receive_stream(self, routing_key):
        # FIXME
        self.channel.basic_consume(callback,
                                   queue='hello',
                                   no_ack=False)

        self.channel.start_consuming()


class UpstreamReleaseMonitoring(object):
    """ messaging for URM """

    def __init__(self):
        self.b = Bunny()
        self.b.register_service("urm")

    def new_release(self):
        pass

    def fetch_releases(self):
        pass