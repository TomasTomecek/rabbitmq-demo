#!/usr/bin/env python
import logging

import pika
from pika import spec


ITERATIONS = 10

logging.basicConfig(level=logging.DEBUG)

confirmed = 0
errors = 0
published = 0

def on_open(connection):
    connection.channel(on_channel_open)



def on_channel_open(channel):
    channel.confirm_delivery(on_delivery_confirmation)
    def on_queue_declare(queue):
        logging.debug(queue)
        global published
        for iteration in xrange(0, ITERATIONS):
            channel.basic_publish('', 'hello',
                                  'message body value',
                                   pika.BasicProperties(content_type='text/plain',
                                                        delivery_mode=1))
            logging.debug("message sent")
            published += 1
    channel.queue_declare(on_queue_declare, 'hello')

def on_delivery_confirmation(frame):
    global confirmed, errors
    if isinstance(frame.method, spec.Basic.Ack):
        confirmed += 1
        logging.info('Received confirmation: %r', frame.method)
    else:
        logging.error('Received negative confirmation: %r', frame.method)
        errors += 1
    if (confirmed + errors) == ITERATIONS:
        logging.info('All confirmations received, published %i, confirmed %i with %i errors', published, confirmed, errors)
        connection.close()


connection = pika.SelectConnection(pika.ConnectionParameters('localhost'), on_open_callback=on_open)
#x = connection.channel()
#x.basic_publish
try:
    connection.ioloop.start()
except KeyboardInterrupt:
    connection.close()
    connection.ioloop.start()
