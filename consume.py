#!/usr/bin/env python

import sys

import pika

if "consume_and_ack" in sys.argv[0]:
    ack = True
    print ' [*] Will ack messages.'
else:
    ack = False
    print ' [*] Will NOT ack messages.'

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    if ack:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print " [x] Acked message with ID %s" % method.delivery_tag

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=False)

channel.start_consuming()
