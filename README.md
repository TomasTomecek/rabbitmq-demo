# RabbitMQ reliability demo


## Start RabbitMQ

```
$ docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 rabbitmq:3
```


## Start producer

Producer is responsible for messages to a queue.

```
$ ./publish.py
```


## Start consumer

Consumer fetches all messages from queue.

```
$ ./consume.py
```

You can see in the output that consumer will not acknowledge messages:

```
 [*] Will NOT ack messages.
```

This means, that when you stop and start consumer again, it will receive all messages, again:

```
$ ./consume.py
```


## Start consumer and ack processed messages

RabbitMQ has a way to let broker know that consumer accepted and processed a message. Let's run improved consumer now:

```
$ ./consume_and_ack.py
```

Output provides info about messages being accepted and acked.

Let's rerun:

```
$ ./consume_and_ack.py
```

Nothing new in the queue, nothing received.


# Resources

 * https://www.rabbitmq.com/tutorials/tutorial-two-python.html
 * http://www.rabbitmq.com/confirms.html

