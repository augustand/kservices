import ujson as json

from utils.net_tool import get_host_ip


async def init_service():
    from utils.app import Application
    app = Application.current()

    _ip = get_host_ip()

    r = app.redis
    st, res = await r.execute("hget", "services.url", "gateway")
    assert st != 0

    _url = "{}:{}".format(_ip, app.port)
    if not res:
        res = [_url]
    else:
        json.loads(res).append(_url)

    app.url = _url
    await r.execute("hset", "services.url", "gateway", json.dumps(res))
