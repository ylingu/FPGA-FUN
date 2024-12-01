from fastapi import HTTPException
from starlette.requests import Request
from utils import Com


def get_com(request: Request) -> Com:
    if not hasattr(request.app.state, "com"):
        raise HTTPException(
            status_code=400,
            detail="COM口尚未创建。请先调用 /api/create_com 创建COM口。",
        )
    return request.app.state.com
