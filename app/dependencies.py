from fastapi import Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from fastapi.security import OAuth2PasswordBearer
import jwt

from .models.models import User
from .db_conf import db_session
db: Session = db_session.session_factory()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
JWT_SECRET = "verysecret"


async def authenticate_user(username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return False
    if not user.verify_password(password):
        return False

    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = db.query(User).filter(
            User.id == payload.get('id')).first()
        print(user)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    return user
