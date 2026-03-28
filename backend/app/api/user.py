from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserUpdate
from app.schemas.common import success
from app.services import user_service

router = APIRouter(prefix="/user", tags=["用户信息"])


@router.get("/info")
def get_user_info(current_user=Depends(get_current_user)):
    return success(user_service.get_user_info(current_user))


@router.put("/info")
def update_user_info(data: UserUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return success(user_service.update_user_info(current_user, data.model_dump(), db))
