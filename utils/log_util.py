# -*- coding: utf-8 -*-
import logging
import sys
import ujson as json

from utils import colors
from utils.app import Application

log = logging.getLogger(__name__)


def log_callback(record):
    _msg = record['msg']
    _c = colors.red if record.get("levelname") == "ERROR" else colors.blue
    if isinstance(_msg, dict):
        __name = "wacai.log.error" if record.get("levelname") == "ERROR" else "wacai.log.info"
        _r = Application.current().redis
        _c = _r.conn()
        if not _c:
            log.error("redis连接失败")
            log.error(_r.error_msg)
            _r.dis_conn()

            sys.stdout.write(
                colors.yellow(
                    "[{name}] [{asctime} {host_ip}] {filename}[{module}.{funcName}][{lineno}]\n".format(
                        **record
                    )
                )
            )
            sys.stdout.write(_c("{levelname}: {msg}\n".format(**record)))
            
        else:
            _c.rpush(__name, json.dumps(record))
    else:
        sys.stdout.write(
            colors.yellow(
                "[{name}] [{asctime} {host_ip}] {filename}[{module}.{funcName}][{lineno}]\n".format(
                    **record
                )
            )
        )
        sys.stdout.write(_c("{levelname}: {msg}\n".format(**record)))
