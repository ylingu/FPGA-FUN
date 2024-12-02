from abc import ABC, abstractmethod
import serial
import numpy as np
import os
import cv2
import shutil


class Connection(ABC):
    @abstractmethod
    def write(self, content: np.ndarray):
        pass


class Com(Connection):
    def __init__(self, port: str | None = None):
        try:
            self.ser = serial.Serial(port, 115200)
        except Exception as e:
            raise e

    def write(self, content: np.ndarray):
        byte_array = np.packbits(content.T.flatten()).tobytes()
        self.ser.write(byte_array)


class VisualConnection(Connection):
    def __init__(self, save_dir: str = "out"):
        self.save_dir = save_dir
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        os.makedirs(self.save_dir, exist_ok=True)
        self.counter = 0

    def write(self, content: np.ndarray):
        image = (content * 255).astype(np.uint8)
        image_path = os.path.join(self.save_dir, f"image_{self.counter}.png")
        cv2.imwrite(image_path, image)
        self.counter += 1
