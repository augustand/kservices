from kservices.config import init_config
from kservices.handlers import init_handle
from kservices.urls import init_url
from utils.app import Application
from utils.redis_util import init_redis

app = Application.instance()

init_handle()
init_config()
init_url()
init_redis()

if __name__ == "__main__":
    import sys
    from os.path import abspath as ap, dirname as dn

    sys.path.append(dn(dn(ap(__file__))))

    app.run(host="0.0.0.0", port=8001, workers=4, debug=False)
