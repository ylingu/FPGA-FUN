import socket
import serial
import numpy as np


def find_free_port():
    """查找一个未被占用的端口"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))  # 让操作系统分配一个可用端口
    address, port = s.getsockname()
    s.close()
    return port


class Com:
    def __init__(
        self, port: str | None = None, baudrate: int = 115200, bytesize: int = 8
    ):
        try:
            self.ser = serial.Serial(port, baudrate, bytesize)
        except Exception as e:
            raise e

    def write(self, content: np.ndarray):
        byte_array = np.packbits(content.T.flatten()).tobytes()
        self.ser.write(byte_array)
