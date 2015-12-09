"""
TODO:
"""
from __future__ import print_function

from copy import deepcopy
import json
import logging

from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container


# create logger
logger = logging.getLogger("m")
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


class Base(object):
    def __init__(self, server, address):
        self.server = "ssl://messaging-devops-broker01.dev1.ext.devlab.redhat.com:5671"
        self.address = address
        logger.debug("initialized")


class Receiver(Base, MessagingHandler):
    """ receive messages """

    def __init__(self, server, address, callback):
        logger.debug("starting initialization")
        self.callback = callback
        Base.__init__(self, server, address)
        MessagingHandler.__init__(self)

    def on_start(self, event):
        logger.debug("opening connection")
        conn = event.container.connect(self.server)
        event.container.create_receiver(conn, self.address)

    def on_message(self, event):
        self.callback(json.loads(event.message.body))
        event.connection.close()


class Sender(Base, MessagingHandler):
    """ send messages """

    def __init__(self, server, address, messages):
        logger.debug("starting initialization")
        self.messages = messages
        Base.__init__(self, server, address)
        MessagingHandler.__init__(self)
        logger.debug("initialized")

    def on_start(self, event):
        logger.debug("opening connection")
        conn = event.container.connect(self.server)
        event.container.create_sender(conn, self.address)

    def on_sendable(self, event):
        for message in self.messages:
            message = json.dumps(message)
            event.sender.send(Message(body=message))
        event.sender.close()


def send_messages(address, messages):
    Container(Sender("not-used", address, messages)).run()

def receive_messages(address, callback):
    Container(Sender("not-used", address, callback)).run()

class UpstreamReleaseMonitoring(object):
    """ messaging for URM """

    SERVICE_NAME = "urm"
    TEMPLATE = {
        "name": None,
        "version": None,
    }

    def new_release(self, package_name, release):
        data = deepcopy(self.TEMPLATE)
        data["name"] = package_name
        data["version"] = release
        address = self.SERVICE_NAME + ".release.new"
        send_messages(address, [data])

    def fetch_releases(self, ack=True):
        def c(m):
            print(m)
        address = self.SERVICE_NAME + ".release.new"
        receive_messages(address, c)

