from sanic.response import json as rep

from kservices.config import init_config
from utils.app import Application
from utils.rabbitmq_util import init_rabbitmq

app = Application.instance()

import ujson as json
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def service_post(req):
    """
    检测服务以及外部接口
    :param req:
    :return:
    """

    _app = Application.current()
    mq = _app.mq

    asyncio.run_coroutine_threadsafe(mq.call("dd"), asyncio.get_event_loop())

    # await mq.call("dd")

    try:
        return rep({"jj": 6})
    except Exception as e:
        print(e)

    return rep(json.dumps({"status": "fail"}))


async def service_get(req):
    """
    检测服务以及外部接口
    :param req:
    :return:
    """

    _app = Application.current()
    mq = _app.mq

    asyncio.run_coroutine_threadsafe(mq.call("dd"), asyncio.get_event_loop())

    # await mq.call("dd")

    try:
        return rep({"jj": 6})
    except Exception as e:
        print(e)

    return rep(json.dumps({"status": "fail"}))


async def run():
    try:
        await app.create_server(host="0.0.0.0", port=8001, debug=False)

        init_config()
        app.route("/api/servies", methods=["POST"])(service_post)
        app.route("/api/servies", methods=["GET"])(service_get)
        init_rabbitmq()

    except Exception as e:
        print(e)


if __name__ == "__main__":
    # import sys
    # from os.path import abspath as ap, dirname as dn
    #
    # sys.path.append(dn(dn(ap(__file__))))
    #
    # app.run(host="0.0.0.0", port=8001, workers=1, debug=True)
    asyncio.ensure_future(run())
    asyncio.get_event_loop().run_forever()
    pass
