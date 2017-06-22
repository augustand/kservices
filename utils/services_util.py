from utils.http_util import request_post
from utils.net_tool import get_host_ip
import ujson as json

async def init_service():
    from utils.app import Application
    app = Application.current()
    app.services = {}

    _ip = get_host_ip()
    r = app.redis

    st, _res = await r.execute("hget", "services.url", app.name)
    assert st != 0

    if _res:
        await request_post(_res, data=json.dumps())

    _url = "http://{}:{}".format(_ip, app.port)
    app.url = _url
    await r.execute("hset", "services.url", "registry", _url)
