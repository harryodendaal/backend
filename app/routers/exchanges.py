import jwt
from ..dependencies import authenticate_user, get_current_user
from ..models.models import Exchange
from ..schema.schema import SchemaExchange
from fastapi import APIRouter, Depends
from passlib.hash import bcrypt
from sqlalchemy.orm.session import Session

from ..db_conf import db_session

JWT_SECRET = "verysecret"

db: Session = db_session.session_factory()

router = APIRouter(
    prefix='/exchanges',
    tags=['exchanges'],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}}
)


@router.post("/add-exchange/", response_model=SchemaExchange)
def add_exchange(exchange: SchemaExchange):
    db_exchange = Exchange(name=exchange.name)
    db.add(db_exchange)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    return db_exchange


@router.get("/exchanges/")
def get_exchanges():
    exchanges = db.query(Exchange).all()

    return exchanges
