import serial
import numpy as np
import os
import cv2
import shutil
import serial.tools.list_ports
from typing import Protocol


class Connection(Protocol):
    def write(self, content: np.ndarray | list[list[int]]):
        ...


class Com:
    def __init__(self, port: str | None = None):
        try:
            self.ser = serial.Serial(port, 115200)
        except Exception as e:
            raise e

    def write(self, content: np.ndarray | list[list[int]]):
        if isinstance(content, list):
            content = np.array(content, dtype=np.uint8)
        byte_array = np.packbits(content.T.flatten()).tobytes()
        self.ser.write(byte_array)


class VisualConnection:
    def __init__(self, save_dir: str = "output"):
        self.save_dir = save_dir
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        os.makedirs(self.save_dir, exist_ok=True)
        self.counter = 0

    def write(self, content: np.ndarray | list[list[int]]):
        if isinstance(content, list):
            content = np.array(content, dtype=np.uint8)
        image = (content * 255).astype(np.uint8)
        image_path = os.path.join(self.save_dir, f"image_{self.counter}.png")
        cv2.imwrite(image_path, image)
        self.counter += 1


def get_available_ports():
    try:
        ports = serial.tools.list_ports.comports()
        serial_ports = [port.name for port in ports]
        return {"serial_ports": serial_ports}
    except Exception as e:
        raise e
