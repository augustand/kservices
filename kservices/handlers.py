import time
import ujson as json
from random import shuffle
from uuid import uuid4

from sanic.response import json as rep

from utils.app import Application
from utils.msg_util import MsgHandler


def __notice_add(data):
    _msgtype = data.get("msgtype", "") or ""
    msgtypes = _msgtype.split("|")

    for msgtype in msgtypes:
        if msgtype == 'notice':
            from bussiness.notice import dingding_post, dingding_msg
            dingding_post(dingding_msg(data.get("notice")))
        elif msgtype == 'log':
            from bussiness.log import log_post
            log_post(data.get("log"))
        else:
            pass


async def notice_add(req):
    """
    :param req:
    :return:
    """
    try:
        from bussiness.notice import notice_add_handle
        _d = json.loads(req.body)
        __notice_add(_d)
    except Exception as e:
        print(e)

    return rep({"status": "ok"})


async def notify_start(req):
    from bussiness.notice import notify_start_handle
    await notify_start_handle()
    return rep({"hello": "world"})


async def notify_stop(req):
    from bussiness.notice import notify_stop_handle
    notify_stop_handle()
    return rep({"hello": "world"})


async def services_post(req):
    app = Application.current()
    r = app.redis
    _id = str(uuid4())
    _id = "".join(shuffle(_id.split("-")))
    errMsg = ""
    status = "ok"
    _now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    await r.execute("hset", "services.ids", )
    try:
        _d = json.loads(req.body)
        _d["id"] = _id
        _d["create_time"] = _now
        await r.execute("lpush", "services.post", json.dumps(_d))
    except Exception as e:
        errMsg = str(e)
        status = "error"
        _d = json.dumps({
            "id": _id,
            "create_time": _now,
            "errMsg": errMsg,
            "data": req.body
        })
        await r.execute("hset", "services.error", _id, _d)
    return rep({"status": status, "id": _id, "errMsg": errMsg})


async def services_get(req):
    app = Application.current()
    r = app.redis
    try:
        _id = req.raw_args.get("id")
        errMsg = ""
        status = "ok"
        st, _res = await r.execute('hmget', 'services.get', *_id.split(","))
        if not st:
            errMsg = _res or ""
            _res = ""
    except Exception as e:
        errMsg = str(e)
        status = "error"
        _res = ""

    return rep({"status": status, "errMsg": errMsg, "data": _res or 0})


async def services_properties_get(req):
    app = Application.current()
    r = app.redis
    try:
        _id = req.raw_args.get("id")
        errMsg = ""
        status = "ok"
        st, _res = await r.execute('hmget', 'services.properties', *_id.split(","))
        if not st:
            errMsg = ""
            _res = ""
    except Exception as e:
        errMsg = str(e)
        status = "error"
        _res = ""

    return rep({"status": status, "errMsg": errMsg, "data": json.loads(_res or "{}")})


async def services_params_get(req):
    app = Application.current()
    r = app.redis
    try:
        _id = req.raw_args.get("id")
        errMsg = ""
        status = "ok"
        st, _res = await r.execute('hmget', 'services.params', *_id.split(","))
        if not st:
            errMsg = ""
            _res = ""
    except Exception as e:
        errMsg = str(e)
        status = "error"
        _res = ""

    return rep({"status": status, "errMsg": errMsg, "data": json.loads(_res or "{}")})


async def ok(req):
    """
    检测服务以及外部接口
    :param req:
    :return:
    """
    app = Application.current()

    r = app.redis

    try:
        st, res = await r.execute('config_get')
        if st:
            redis_status = "ok"
            print("redis config:\n", res)
        else:
            print("redis exception\n", res)
            redis_status = res
    except Exception as e:
        redis_status = str(e)
        print(e)

    return rep({
        "redis_status": redis_status,
        "timers": app.timers.keys()
    })


def init_handle():
    app = Application.current()
    app.handler = MsgHandler()
