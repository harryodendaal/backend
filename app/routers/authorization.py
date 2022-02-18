import jwt
from ..dependencies import authenticate_user, get_current_user
from ..models.models import User
from ..schema.schema import SchemaUserIn, SchemaUserOut
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from sqlalchemy.orm.session import Session

from ..db_conf import db_session

JWT_SECRET = "verysecret"

db: Session = db_session.session_factory()

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {"description": "Not Found"}}
)


@router.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        return {"error": "invalid credentials"}

    token = jwt.encode(
        {"username": user.username, "id": user.id}, JWT_SECRET)

    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/create-user', response_model=SchemaUserOut)
async def create_user(user: SchemaUserIn):
    user_obj = User(username=user.username,
                    password_hash=bcrypt.hash(user.password_hash))
    db.add(user_obj)
    try:
        db.commit()
    except:
        db.rollback()

        raise
    return {"username": user.username}


@router.get('/users/me', response_model=SchemaUserOut)
async def get_user(user: SchemaUserIn = Depends(get_current_user)):
    # print("this is username", user.username)
    return {"username": user.username}
