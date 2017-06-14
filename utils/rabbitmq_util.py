import socket

import aioamqp


class RabbitMQManager(object):
    def __init__(self, config=None):
        self.cfg = config

    async def error_callback(self, exception):
        print(exception)

    async def conn(self):
        return await self.__conn()

    async def __conn(self):
        try:
            c = self.cfg
            transport, protocol = await aioamqp.connect(
                host=c.get("host", 'localhost'),
                port=c.get("port", 5672),
                login=c.get("login", 'guest'),
                password=c.get("password", 'guest'),
                virtualhost=c.get("virtualhost", "/"),
                on_error=self.error_callback,
            )

            return protocol
        except Exception as e:
            print(e)

    async def __producer_conn(self, exchange_name='test', msgtype='topic'):
        try:
            c = self.cfg
            transport, protocol = await aioamqp.connect(
                host=c.get("host", 'localhost'),
                port=c.get("port", 5672),
                login=c.get("login", 'guest'),
                password=c.get("password", 'guest'),
                virtualhost=c.get("virtualhost", "/"),
                on_error=self.error_callback,
                client_properties={
                    'program_name': "test",
                    'hostname': socket.gethostname(),
                },
            )

            channel = await protocol.channel()
            await channel.queue_declare(durable=True)
            await channel.exchange_declare(exchange_name, msgtype, durable=True)
            return channel
        except aioamqp.AmqpClosedConnection as e:
            print("closed connections")
            print(e)

    async def __callback(self, channel, body, envelope, properties):
        print(channel)
        print(body)
        print(envelope)
        print(properties)

    async def __consumer_conn(self, exchange_name='test', msgtype='topic', routing_key=None, func=None):
        func = func or self.__callback

        try:
            c = self.cfg
            transport, protocol = await aioamqp.connect(
                host=c.get("host", 'localhost'),
                port=c.get("port", 5672),
                login=c.get("login", 'guest'),
                password=c.get("password", 'guest'),
                virtualhost=c.get("virtualhost", "/"),
                on_error=self.error_callback,
                client_properties={
                    'program_name': "test",
                    'hostname': socket.gethostname(),
                }
            )

            channel = await protocol.channel()
            await channel.exchange_declare(exchange_name, msgtype)
            result = await channel.queue(durable=True)
            queue_name = result['queue']
            await channel.queue_bind(
                exchange_name,
                queue_name,
                routing_key
            )

            await channel.basic_consume(func, queue_name=queue_name)
        except Exception as e:
            print("closed connections")
            print(e)


def init_rabbitmq():
    from utils.app import Application
    app = Application.current()
    app.redis = RabbitMQManager(config=app.config.get("REDIS"))


async def _p():
    r = RabbitMQManager(config={"host": 'localhost'})
    conn = await r.conn()
    channel = await conn.channel()
    # await channel.queue_declare(queue_name='test',durable=True)
    await channel.exchange_declare("services", 'topic', durable=True)
    await channel.publish("hello world", 'services', "test.test")
    await channel.publish("hello world", 'services', "test.test1")


async def _c():
    r = RabbitMQManager(config={"host": 'localhost'})
    conn = await r.conn()
    channel = await conn.channel()

    await channel.exchange_declare('services', 'topic', durable=True)
    await channel.queue_declare(queue_name='test', durable=True)
    await channel.queue_declare(queue_name='test1', durable=True)
    q = await channel.queue_declare(exclusive=True)
    print(q)
    await channel.queue_bind(
        'test',
        'services',
        "test.test"
    )
    await channel.queue_bind(
        'test1',
        'services',
        "test.test1"
    )

    async def __callback(ch, body, envelope, properties):
        print(ch)
        print(body)
        print(envelope.consumer_tag)
        print(envelope.delivery_tag)
        print(properties)

        await ch.basic_client_ack(envelope.delivery_tag)
        print()
        return

    await channel.basic_consume(__callback, queue_name='test')
    await channel.basic_consume(__callback, queue_name='test1')


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(_p())
    asyncio.ensure_future(_p())

    asyncio.ensure_future(_c())

    loop.run_forever()

    # 一个服务端，或者说一个消费端至少包含业务处理和配置
    # 业务处理处理业务本身的任务，一个服务一个单独的队列
    # 所有的服务共享一个exchange(topic)
    # 每一个服务单独一个exchange(fanout)用来处理自身的配置信息,所有连接上的都会自动获取信息
    # 用排他性队列来处理配置，这样就不用关心你申请的是什么队列了

