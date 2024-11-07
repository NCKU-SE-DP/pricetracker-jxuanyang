from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta

from .models import User  # 假設 User 模型在 auth.models 中

# 設定密碼加密方式
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "1892dhianiandowqd0n"
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    """驗證密碼是否正確"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    """將密碼加密"""
    return pwd_context.hash(password)

def check_user_password_is_correct(db: Session, username: str, password: str):
    """驗證使用者的帳號密碼"""
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    """創建存取權杖"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
