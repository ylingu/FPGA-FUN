import socket


def find_free_port():
    """查找一个未被占用的端口"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))  # 让操作系统分配一个可用端口
    address, port = s.getsockname()
    s.close()
    return port
