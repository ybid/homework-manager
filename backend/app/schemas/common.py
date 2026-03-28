from pydantic import BaseModel
from typing import Any, Optional, List


class Response(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class PaginatedResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict = {
        "list": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 0,
            "total_pages": 0,
        }
    }


def success(data: Any = None, message: str = "success"):
    return {"code": 0, "message": message, "data": data}


def fail(message: str, code: int = 400):
    return {"code": code, "message": message, "data": None}


def paginate(items: List[Any], total: int, page: int, page_size: int):
    return {
        "code": 0,
        "message": "success",
        "data": {
            "list": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
            }
        }
    }
