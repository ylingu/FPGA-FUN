from pydantic import BaseModel

class Matrix(BaseModel):
    matrix: list[list[int]]
