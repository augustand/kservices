import ujson as json

import aiozmq.rpc


class Handler(aiozmq.rpc.AttrHandler):
    def __init__(self):
        self.connected = False

    @aiozmq.rpc.method
    def remote_func(self, step, a: int, b: int):
        self.connected = True
        print("HANDLER", step, a, b)
        return a + b


async def init_zmq_server():
    from utils.app import Application
    app = Application.current()
    r = app.redis

    sub = await aiozmq.rpc.serve_pubsub(
        Handler(),
        subscribe='registry',
        bind='tcp://*:*',
        log_exceptions=True,
        timeout=1,
    )

    addr = list(sub.transport.bindings())[0]
    await r.execute("hset", "services.url", "registry", addr)


async def init_zmq_client():
    from utils.app import Application
    app = Application.current()
    r = app.redis

    st, res = await r.execute("hget", "services.url", "gateway.monitor")
    res = json.loads(res)

    app.gateway_monitor = await aiozmq.rpc.connect_pubsub(
        timeout=1,
        connect=res
    ).publish("gateway.monitor")
