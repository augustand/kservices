def init_url():

    from utils.app import Application
    app = Application.current()

    from kservices.handlers import notice_add, notify_start, notify_stop, ok
    app.route("/api/notice", methods=["POST"])(notice_add)
    app.route("/api/notify", methods=["POST"])(notify_start)
    app.route("/api/notify", methods=["DELETE"])(notify_stop)
    app.route("/service/status", methods=["GET"])(ok)
    app.route("/", methods=["GET"])(ok)
