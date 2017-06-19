import asyncio
from uuid import uuid4

import aioamqp


class RabbitMQManager(object):
    def __init__(self, config=None):
        self.cfg = config
        self.transport = None
        self.protocol = None
        self.channel = None
        self.callback_queue = None
        # self.waiter = asyncio.Event()
        self.response=None

    async def error_callback(self, exception):
        print(exception)

    async def __client(self):
        try:
            if self.protocol:
                return

            c = self.cfg
            transport, protocol = await aioamqp.connect(
                # host=c.get("host", 'localhost'),
                # port=c.get("port", 5672),
                # login=c.get("login", 'guest'),
                # password=c.get("password", 'guest'),
                # virtualhost=c.get("virtualhost", "/"),
                on_error=self.error_callback,
            )

            print(protocol)

            self.protocol = protocol
            self.channel = await self.protocol.channel()
            result = await self.channel.queue_declare(queue_name='', exclusive=True)
            self.callback_queue = result['queue']
            await self.channel.basic_consume(
                self.rpc_client_response,
                no_ack=True,
                queue_name=self.callback_queue,
            )

        except Exception as e:
            print(e)
            print("close\n\n\n\n")

    async def rpc_client_response(self, channel, body, envelope, properties):
        if self.corr_id == properties.correlation_id:
            self.response = body
        # self.waiter.set()

    async def call(self, data):
        await self.__client()

        self.response = None
        self.corr_id = str(uuid4())
        await self.channel.basic_publish(
            payload=data,
            exchange_name='',
            routing_key='rpc_queue',
            properties={
                'reply_to': self.callback_queue,
                'correlation_id': self.corr_id,
            },
        )
        # await self.waiter.wait()
        return self.corr_id


def init_rabbitmq():
    from utils.app import Application
    app = Application.current()
    app.mq = RabbitMQManager(config=app.config.get("RABBITMQ"))
