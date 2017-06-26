import asyncio

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def init_app():
    from kservices.config import init_config
    from kservices.handlers import init_handle
    from kservices.urls import init_url
    from utils.redis_util import init_redis

    init_handle()
    init_config()
    init_url()
    init_redis()
