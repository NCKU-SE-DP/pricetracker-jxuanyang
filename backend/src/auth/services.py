from datetime import datetime, timedelta
from jose import jwt
from fastapi import Depends
from src.models import User
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from .dependencies import oauth2_scheme

# 初始化資料庫引擎
engine = create_engine("sqlite:///news_database.db", echo=True)

def session_opener():
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user_token(
    token = Depends(oauth2_scheme),
    db = Depends(session_opener)
):
    payload = jwt.decode(token, '1892dhianiandowqd0n', algorithms=["HS256"])
    return db.query(User).filter(User.username == payload.get("sub")).first()


