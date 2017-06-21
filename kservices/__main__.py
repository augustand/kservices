# -*- coding:utf-8 -*-
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
@click.option('--host', '-h', default='0.0.0.0', help=u'主机', show_default=True)
@click.option('--port', '-p', default=8080, help=u'端口', show_default=True)
def main(env, host, port):
    """启动服务"""

    from signal import signal, SIGTERM, SIGINT, SIGQUIT
    signal(SIGTERM, term_sig_handler)
    signal(SIGINT, term_sig_handler)
    signal(SIGQUIT, term_sig_handler)

    from utils.app import Application
    app = Application.instance()

    app.env = env
    app.port = port

    from kservices.main import init_app
    init_app()

    app.run(host="0.0.0.0", port=port, workers=1, debug=False if env == 'pro' else True)


if __name__ == "__main__":
    main()
