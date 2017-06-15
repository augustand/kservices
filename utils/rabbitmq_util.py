import socket

import aioamqp
import msgpack


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


async def __init_rabbitmq():
    from utils.app import Application
    app = Application.current()
    r = RabbitMQManager(config=app.config.get("REDIS"))
    conn = await r.conn()

    service_name = app.config.get("NAME")
    print(service_name)

    # 初始化配置
    cfg_ch = await conn.channel()
    await cfg_ch.exchange_declare(service_name, 'fanout', durable=True)
    q = await cfg_ch.queue_declare(exclusive=True)
    await cfg_ch.queue_bind(
        q['queue'],
        service_name,
        ''
    )

    async def __callback(ch, body, envelope, properties):
        mth = envelope.routing_key.split(service_name).pop()

        h = app.handler

        if not hasattr(h, mth):
            return

        await getattr(h, mth)(msgpack.loads(body))

        st, _res = await ch.basic_client_ack(envelope.delivery_tag)
        if st:
            await ch.basic_client_ack(envelope.delivery_tag)
        else:
            pass
            # 执行失败,发送失败原因到其他的服务中，或者到其他的接口，数据库中


    await cfg_ch.basic_consume(__callback, queue_name=q['queue'])

    # 初始化应用
    service_ch = await conn.channel()
    await service_ch.exchange_declare('services', 'topic', durable=True)
    await service_ch.queue_declare(queue_name=service_name, durable=True)
    await service_ch.queue_bind(
        service_name,
        'services',
        'services.{}.#'.format(service_name)
    )

    app.mq = r


def init_rabbitmq():
    asyncio.ensure_future(__init_rabbitmq())


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
        key = envelope.routing_key
        exchange_name = envelope.exchange_name

        print(body)
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

'''
channel ['_loop', '_send_channel_close_ok', '_set_waiter', '_write_frame', '_write_frame_awaiting_response',
    'basic_cancel', 'basic_cancel_ok', 'basic_client_ack', 'basic_client_nack', 'basic_consume', 'basic_consume_ok',
    'basic_deliver', 'basic_get', 'basic_get_empty', 'basic_get_ok', 'basic_publish', 'basic_qos', 'basic_qos_ok',
    'basic_recover', 'basic_recover_async', 'basic_recover_ok', 'basic_reject', 'basic_server_ack', 'basic_server_nack',
    'cancelled_consumers', 'channel_id', 'close', 'close_event', 'close_ok', 'confirm_select', 'confirm_select_ok',
    'connection_closed', 'consumer_callbacks', 'consumer_queues', 'delivery_tag_iter', 'dispatch_frame', 'exchange',
    'exchange_bind', 'exchange_bind_ok', 'exchange_declare', 'exchange_declare_ok', 'exchange_delete',
    'exchange_delete_ok', 'exchange_unbind', 'exchange_unbind_ok', 'flow', 'flow_ok', 'is_open', 'last_consumer_tag',
    'open', 'open_ok', 'protocol', 'publish', 'publisher_confirms', 'queue', 'queue_bind', 'queue_bind_ok',
    'queue_declare', 'queue_declare_ok', 'queue_delete', 'queue_delete_ok', 'queue_purge', 'queue_purge_ok',
 'queue_unbind', 'queue_unbind_ok', 'response_future', 'server_basic_cancel', 'server_channel_close']

envelope ['consumer_tag', 'delivery_tag', 'exchange_name', 'is_redeliver', 'routing_key']

properties ['app_id', 'cluster_id', 'content_encoding', 'content_type', 'correlation_id', 'delivery_mode',
    'expiration', 'headers', 'message_id', 'priority', 'reply_to', 'timestamp', 'type', 'user_id']
'''
