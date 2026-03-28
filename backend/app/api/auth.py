from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserLogin, UserUpdate
from app.schemas.common import success, fail
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        result = await user_service.login(data.code, db)
        return success(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
