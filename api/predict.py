import cv2
import numpy as np
import onnxruntime
from pathlib import Path

BASE_PATH = Path(__file__).parent

model = onnxruntime.InferenceSession(BASE_PATH / "model.onnx")
figures: np.ndarray = np.load(BASE_PATH / "figures.npy")


def predict_number(content: bytes) -> tuple[int, np.ndarray]:
    image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_GRAYSCALE)
    image = np.expand_dims(image, axis=0)
    image = np.expand_dims(image, axis=0)
    image = image.astype(np.float32)
    image = image / 255.0
    inputs = {
        model.get_inputs()[0].name: image,
        model.get_inputs()[1].name: np.array([image.shape[2]]),
    }
    out = model.run(None, inputs)
    logits = np.transpose(out[0], (0, 2, 1))
    sequence: np.ndarray = np.argmax(logits, axis=1)
    word: list[np.int64] = [k + 1 for k in sequence[0] if k != 10]
    result = int(word[0])
    return result, figures[result]
