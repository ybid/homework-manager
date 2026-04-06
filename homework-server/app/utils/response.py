from __future__ import annotations

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(self, code: int = 10000, message: str = "服务器内部错误", status_code: int = 200):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthException(AppException):
    def __init__(self, message: str = "未授权，请先登录"):
        super().__init__(code=10001, message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "无权限执行此操作"):
        super().__init__(code=10003, message=message, status_code=403)


class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=10004, message=message, status_code=404)


class ValidationException(AppException):
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(code=10002, message=message, status_code=422)


class BusinessException(AppException):
    """Business logic exception (200 status but non-zero code)."""

    def __init__(self, code: int = 20000, message: str = "业务处理失败"):
        super().__init__(code=code, message=message, status_code=200)


def success_response(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def error_response(code: int = 10000, message: str = "error", data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "success",
) -> dict:
    return {
        "code": 0,
        "message": message,
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
            },
        },
    }
