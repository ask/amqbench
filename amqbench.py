#!/usr/bin/env python
import os
import socket
import sys

from time import time

import anyjson
from anyjson import serialize, deserialize
from kombu import BrokerConnection, Exchange, Queue, Producer, Consumer

str_to_bool = {"yes": True, "no": False,
               "1": True, "0": False,
               "true": True, "false": False}

JSONIMP = os.environ.get("JSONIMP")
if JSONIMP:
    anyjson.force_implementation(JSONIMP)
MESSAGE = {"task": "foo.bar", "args": (1, 2), "kwargs": {"callback": "foo"}}
DURABLE = str_to_bool[os.environ.get("DURABLE", "yes").lower()]
DM = int(os.environ.get("DM", 2))  # delivery-mode


class _Consumer(Consumer):

    def __init__(self, *args, **kwargs):
        self.i = 0
        super(_Consumer, self).__init__(*args, **kwargs)

    def _receive_callback(self, raw_message):
        self.i += 1
        if not self.i % 10000:
            print(self.i)


def _declare(chan, name, durable=DURABLE):
    chan.exchange_declare(exchange=name, type="direct", durable=durable,
                          auto_delete=True)
    chan.queue_declare(queue=name, durable=durable, auto_delete=True)
    chan.queue_bind(queue=name, exchange=name, routing_key=name)
    return chan


def _kpublish(n, name, conn, durable=DURABLE, delivery_mode=DM):
    _cleanup(conn.clone, name)
    channel = conn.channel()
    exchange = Exchange(name, type="direct", auto_declare=False,
                              durable=durable, auto_delete=True)
    Queue(name, exchange, name, durable=durable,
          auto_delete=True)(channel).declare()
    producer = Producer(channel, exchange, serializer="json")
    message = MESSAGE

    start = time()
    for i in xrange(n + 2000):
        producer.publish(message, routing_key=name,
                                  delivery_mode=delivery_mode)
    print(time() - start)


def _kconsume(n, name, conn, durable=DURABLE):
    channel = conn.channel()
    exchange = Exchange(name, type="direct", durable=durable,
                        auto_delete=True)
    queue = Queue(name, exchange, name, durable=durable,
                  auto_delete=True)
    consumer = Consumer(channel, queue)
    ucon = conn.connect()

    i = [0]

    def callback(message_data, message=None):
        i[0] += 1
        if not i[0] % 10000:
            print(i[0])

    consumer.register_callback(callback)
    consumer.consume(no_ack=True)

    start = time()
    while i[0] < n:
        try:
            conn.drain_events()
        except socket.timeout:
            pass
    print(time() - start)

def _publish(n, Connection, Message, name):
    props = {"delivery_mode": DM}
    kwargs = {"properties": props}
    if "amqplib" in repr(Message):
        kwargs = props
    _cleanup(Connection, name)
    conn = Connection()
    chan = conn.channel()
    chan = _declare(chan, name)

    if name == 'librabbitmq':
        _Message = lambda: (serialize(MESSAGE), props)
    else:
        _Message = lambda: Message(serialize(MESSAGE), **kwargs)


    start = time()
    for i in xrange(n + 2000):
        if not i % 10000:
            print(i)
        message = _Message()
        chan.basic_publish(message, exchange=name, routing_key=name)
    print(time() - start)


def _cleanup(Connection, name, _chan=None):
    pass

def _consume(n, Connection, name):
    conn = Connection()
    chan = conn.channel()
    chan = _declare(chan, name)

    i = [0]
    def callback(message):
        assert len(message.body) > 10
        i[0] += 1
        if not i[0] % 10000:
            print(i[0])
        deserialize(message.body)
        #chan.basic_ack(message.delivery_info["delivery_tag"])

    chan.basic_consume(queue=name, no_ack=True, callback=callback)

    if hasattr(conn, "drain_events"):
        wait = conn.drain_events
    else:
        wait = chan.wait

    start = time()
    while i[0] < n:
        wait()
    print(time() - start)

    chan.close()
    conn.close()


class amqplib(object):

    def publish(self, n=52000):
        from amqplib.client_0_8 import Connection, Message
        _publish(n, Connection, Message, "amqplib")

    def consume(self, n=52000):
        from amqplib.client_0_8 import Connection
        _consume(n, Connection, "amqplib")


class kamqp(object):

    def publish(self, n=52000):
        from kamqp.client_0_8 import Connection, Message
        _publish(n, Connection, Message, "kamqp")

    def consume(self, n=52000):
        from kamqp.client_0_8 import Connection
        _consume(n, Connection, "kamqp")

class librabbitmq(object):

    def publish(self, n=52000):
        from librabbitmq import Connection, Message
        _publish(n, Connection, Message, "librabbitmq")

    def consume(self, n=52000):
        from librabbitmq import Connection
        _consume(n, Connection, "librabbitmq")


class KombuBench(object):
    transport = None

    def publish(self, n=52000):
        _kpublish(n, self.__class__.__name__,
                  BrokerConnection(transport=self.transport))

    def consume(self, n=52000):
        _kconsume(n, self.__class__.__name__,
                  BrokerConnection(transport=self.transport))


class klibrabbitmq(KombuBench):
    transport = "librabbitmq"


class kamqplib(KombuBench):
    transport = "amqplib"


class kmemory(KombuBench):
    transport = "memory"

    def bench(self, n=52000):
        self.publish(n)
        self.consume(n)


types = {"amqplib": amqplib(),
         "kamqp": kamqp(),
         "librabbitmq": librabbitmq(),
         "klibrabbitmq": klibrabbitmq(),
         "kamqplib": kamqplib(),
         "kmemory": kmemory()}


if __name__ == "__main__":
    getattr(types[sys.argv[1]], sys.argv[2])()
