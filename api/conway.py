import numpy as np


def matrix_transpose(matrix: list[list[int]]) -> np.ndarray:
    return np.array(matrix, dtype=np.uint8).T
