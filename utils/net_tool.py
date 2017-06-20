# -*- coding:utf-8 -*-



def get_host_user():
    """
    获得主机用户
    :return:
    """
    try:
        import getpass
        return 1, getpass.getuser()
    except Exception as e:
        return 0, str(e)


def get_host_ip():
    """
    获得主机本地IP
    :return:
    """
    import socket
    return socket.gethostbyname(socket.getfqdn(socket.gethostname()))


def get_host_name():
    """
    获得主机名
    :return:
    """
    try:
        import socket
        return 1, socket.getfqdn(socket.gethostname())
    except Exception as e:
        return 0, str(e)
