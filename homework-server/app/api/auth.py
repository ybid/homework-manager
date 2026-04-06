from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import LoginRequest, LoginResponse
from app.services.user_service import login_by_code
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """微信小程序登录"""
    result = await login_by_code(db, req.code)
    return success_response(data=LoginResponse(**result).model_dump())
