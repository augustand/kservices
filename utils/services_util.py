from utils.net_tool import get_host_ip


async def init_service():
    from utils.app import Application
    app = Application.current()

    _ip = get_host_ip()

    r = app.redis
    app.url = "{}:{}".format(_ip, app.port)
    st, _ = await r.execute("sadd", "{}.url".format(app.name), app.url)
    assert st != 0
