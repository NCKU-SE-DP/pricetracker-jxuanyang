from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.auth.services import session_opener
from src.auth.schemas import UserAuthSchema
from src.auth.services import create_access_token
from src.models import User
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/users/register")
def register_user(user: UserAuthSchema, db: Session = Depends(session_opener)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
