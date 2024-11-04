from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.auth.schemas import UserAuthSchema
from src.auth.services import create_access_token

router = APIRouter()

@router.post("/register")
def register_user(user: UserAuthSchema, db: Session = Depends(SessionLocal)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return db_user
