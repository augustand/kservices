import ujson as json

from sanic.response import json as rep

from utils.app import Application


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
