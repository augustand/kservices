# -*- coding:utf-8 -*-
import asyncio
import sys
from os.path import abspath as ap, dirname as dn

sys.path.append(dn(dn(ap(__file__))))

import click

click.disable_unicode_literals_warning = True


def term_sig_handler(signum, frame):
    import logging
    logging.getLogger().info('catched singal: {},{}'.format(signum, frame))
    sys.exit(0)


@click.command()
@click.option('--env', '-e', default='local', help=u'开发环境设置', show_default=True)
@click.option('--port', '-p', default=8080, help=u'端口', show_default=True)
def main(env, port):
    """启动服务"""

    from signal import signal, SIGTERM, SIGINT, SIGQUIT
    signal(SIGTERM, term_sig_handler)
    signal(SIGINT, term_sig_handler)
    signal(SIGQUIT, term_sig_handler)

    from utils.app import Application
    app = Application.instance()

    app.env = env
    app.port = port
    app.name = "score"

    from kservices.main import init_app
    init_app()

    asyncio.ensure_future(app.create_server(host="0.0.0.0", port=port, debug=False if env == 'pro' else True))
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
