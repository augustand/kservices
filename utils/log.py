# -*- coding:utf-8 -*-

'''
This library is provided to allow standard python logging
to output log data as JSON formatted strings
'''
import logging
import sys
import time

from utils import colors


class JsonHandler(logging.Handler):
    def __init__(self, level=logging.INFO, emit_callback=None, key_words=None):
        self.emit_callback = emit_callback
        self.key_words = key_words
        logging.Handler.__init__(self, level=level)
        from utils.net_tool import get_host_ip
        self.host_ip = get_host_ip()

    def emit(self, record):
        _a = {}
        _r = record.__dict__
        for key in self.key_words:
            _d = _r.get(key)
            if _d:
                _a[key] = _d

        _a["host_ip"] = self.host_ip

        timeArray = time.localtime(record.created)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        _a["asctime"] = otherStyleTime
        self.emit_callback(_a)


class KLog(object):
    def __init__(self, key_words=None, callback=None):
        self.callback = callback
        from kservices.const import base_log_key_words
        self.key_words = key_words or base_log_key_words
        self.log_format = ' '.join((lambda x: ['%({0:s})'.format(i) for i in x])(self.key_words))

    def init_log(self):
        logger = logging.getLogger()
        logger.addHandler(JsonHandler(
            emit_callback=self.__callback,
            key_words=self.key_words))
        logger.setLevel(logging.INFO)

    def set_callback(self, callback):
        self.callback = callback
        return self

    def __callback(self, record):
        if not self.callback:

            sys.stdout.write(colors.yellow(
                "[{name}] [{asctime} {host_ip}] {filename}[{module}.{funcName}][{lineno}]\n".format(
                    **record
                ))
            )

            levelname = record.get("levelname")
            _c = colors.red if levelname == "ERROR" else colors.blue

            _msg = record['msg']
            if isinstance(_msg, dict):
                sys.stdout.write(_c("{levelname}:\n".format(**record)))
                for k, v in _msg.items():
                    sys.stdout.write(_c("   {0}:{1}\n".format(k, v)))
            else:
                sys.stdout.write(_c("{levelname}: {msg}\n".format(**record)))
        else:
            self.callback(record)


if __name__ == '__main__':
    def hello(record):
        print(record)


    KLog().init_log()

    logger = logging.getLogger("hello")
    logger.error("classic mebhhhhhhhhhhhhhhhh到底hhhssage")
    logger.info("classic mebhhhhhhhhhhhhhhhh到底hhhssage")
    logger.info({"special": "value", "run": 12, "是谁": "的肚饿护额"})
    logger.error({"special": "value", "run": 12, "是谁": "的肚饿护额"})
