import jwt
from app.dependencies import get_current_user
from ..models.models import Symbol
from ..schema.schema import SchemaSymbol
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from ..db_conf import db_session

JWT_SECRET = "verysecret"

db: Session = db_session.session_factory()

router = APIRouter(
    prefix='/symbols',
    tags=['symbols'],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}}
)


@router.post("/add-symbol/", response_model=SchemaSymbol)
def add_symbol(symbol: SchemaSymbol):
    db_symbol = Symbol(name=symbol.name, exchange_id=symbol.exchange_id)
    db.add(db_symbol)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    return db_symbol


@router.get("/symbols/")
def get_symbols():
    symbols = db.query(Symbol).all()

    return symbols
