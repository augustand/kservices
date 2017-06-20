# -*- coding: utf-8 -*-


class Config(object):
    NAME = "wacai"
    DEBUG = True
    SECRET_KEY = '123456@#$%^&*('
    PORT = 8080


class LocalConfig(Config):
    REDIS = {
        "address": ("127.0.0.1", 6379),
    }

    # mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    MONGODB_URI = "mongodb://localhost:27017"
    MONGODB_DB = "kservices"


class DevConfig(Config):
    REDIS = {
        "address": ("192.168.202.205", 9221),
        "password": None,
        "db": 0
    }


class UatConfig(Config):
    DEBUG = False
    REDIS = {
        "address": ("192.168.202.214", 9221),
        "password": None,
        "db": 0
    }


class ProConfig(Config):
    DEBUG = False
    REDIS = {
        "address": ("172.16.10.19", 9221),
        "password": None,
        "db": 0
    }


def init_config():
    from utils.app import Application
    app = Application.current()

    if not hasattr(app, "timers"):
        app.timers = {}

    import os
    from kservices.const import Env

    _e = os.environ.get("app_env", Env.local)
    if _e == Env.local:
        _f = LocalConfig()
    elif _e == Env.dev:
        _f = DevConfig()
    elif _e == Env.uat:
        _f = UatConfig()
    elif _e == Env.production:
        _f = ProConfig()
    else:
        _f = LocalConfig()

    app.config.from_object(_f)
    app.debug = _f.DEBUG

    app.port = int(os.getenv("service_port", 8080))
    app.workers = int(os.getenv("service_workers", 1))
