from fastapi import HTTPException
from starlette.requests import Request
from connection import Connection, VisualConnection


def get_connection(request: Request) -> Connection:
    if not hasattr(request.app.state, "con"):
        request.app.state.con = VisualConnection()
        raise HTTPException(
            status_code=400,
            detail="The COM port has not been created yet, use VisualConnection",
        )
    return request.app.state.con
