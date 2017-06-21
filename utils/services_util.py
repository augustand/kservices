from utils.net_tool import get_host_ip


async def init_service():
    from utils.app import Application
    app = Application.current()
    app.services = {}

    _ip = get_host_ip()
    r = app.redis
    _url = "http://{}:{}".format(_ip, app.port)
    app.url = _url
    await r.execute("hset", "services.url", "registry", _url)
