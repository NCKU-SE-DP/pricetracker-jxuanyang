from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

def get_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    try:
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        return user
    except:
        return None
