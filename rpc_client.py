#!/usr/bin/env python

"""
    RPC client, aioamqp implementation of RPC examples from RabbitMQ tutorial
"""

import asyncio
import uuid

import aioamqp
import time


class FibonacciRpcClient(object):
    def __init__(self):
        self.transport = None
        self.protocol = None
        self.channel = None
        self.callback_queue = None
        self.waiter = asyncio.Event()

    @asyncio.coroutine
    def connect(self):
        """ an `__init__` method can't be a coroutine"""
        self.transport, self.protocol = yield from aioamqp.connect()
        self.channel = yield from self.protocol.channel()

        result = yield from self.channel.queue_declare(queue_name='', exclusive=True)
        self.callback_queue = result['queue']

        yield from self.channel.basic_consume(
            self.on_response,
            no_ack=True,
            queue_name=self.callback_queue,
        )

    @asyncio.coroutine
    def on_response(self, channel, body, envelope, properties):
        if self.corr_id == properties.correlation_id:
            self.response = body

        self.waiter.set()

    @asyncio.coroutine
    def call(self, data):
        if not self.protocol:
            yield from self.connect()
        self.response = None
        self.corr_id = str(uuid.uuid4())
        yield from self.channel.basic_publish(
            payload=str(data),
            exchange_name='',
            routing_key='rpc_queue',
            properties={
                'reply_to': self.callback_queue,
                'correlation_id': self.corr_id,
            },
        )
        yield from self.waiter.wait()

        yield from self.protocol.close()
        return self.response


@asyncio.coroutine
def rpc_client():
    fibonacci_rpc = FibonacciRpcClient()
    print(" [x] Requesting fib(30)")
    response = yield from fibonacci_rpc.call(30)
    print(" [.] Got %r" % response)

# asyncio.ensure_future(rpc_client())
# asyncio.get_event_loop().run_forever()
while 1:
    print(uuid.uuid4())
    time.sleep(1)
    asyncio.get_event_loop().run_until_complete(rpc_client())


