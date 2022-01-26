# other schedulers are available
import json
import os
import time
import jwt
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import pandas as pd
import pytz
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
# from fastapi_sqlalchemy import DBSessionMiddleware, db


from helper_functions import changeCandleTimeFrame, getExchangeObject
from Models.models import Exchange as ModelExchange
from Models.models import MinuteBars as ModelMinuteBars
from Models.models import Symbol as ModelSymbol
from Models.models import User as ModelUser
from schema import Exchange as SchemaExchange
from schema import MinuteBars as SchemaMinuteBars
from schema import Symbol as SchemaSymbol
from schema import UserIn, UserOut
from sqlalchemy.orm.session import Session
from db_conf import db_session

db: Session = db_session.session_factory()
load_dotenv(".env")


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TIME_INTERVAL_IN_SEC = 15
JWT_SECRET = "verysecret"


async def getCandleStickData():
    exchanges = db.query(ModelExchange).all()
    for exchange in exchanges:
        exchange_id = exchange.id
        exchange = getExchangeObject(exchange)

        symbols = db.query(ModelSymbol).filter(
            ModelSymbol.exchange_id == exchange_id)
        for symbol in symbols:  # BTC/USDT ETH/USDT BIT/USDT
            time.sleep(exchange.rateLimit / 1000)
            data = await exchange.fetch_ohlcv(
                symbol.name, '1m', limit=100)

            df = pd.DataFrame(data)
            col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
            df.columns = col_names

            for col in col_names:
                df[col] = df[col].astype(float)

            latestKline = db.query(
                ModelMinuteBars).filter(ModelMinuteBars.symbol_id == symbol.id).order_by(ModelMinuteBars.id.desc()).first()

            CryptoDataEmpty = False
            if latestKline == None:
                CryptoDataEmpty = True
            insertRest = False

            for each_line in df.index:
                dfTime = df['time'].loc[each_line]
                if not CryptoDataEmpty:
                    if insertRest or (latestKline.date < dfTime):
                        open = df['open'].loc[each_line]
                        high = df['high'].loc[each_line]
                        low = df['low'].loc[each_line]
                        close = df['close'].loc[each_line]
                        volume = df['volume'].loc[each_line]
                        kline = ModelMinuteBars(
                            date=dfTime, open=open, high=high, low=low, close=close, volume=volume, symbol_id=symbol.id)
                        db.add(kline)
                        insertRest = True
                else:
                    open = df['open'].loc[each_line]
                    high = df['high'].loc[each_line]
                    low = df['low'].loc[each_line]
                    close = df['close'].loc[each_line]
                    volume = df['volume'].loc[each_line]
                    kline = ModelMinuteBars(
                        date=dfTime, open=open, high=high, low=low, close=close, volume=volume, symbol_id=symbol.id)
                    db.add(kline)

            try:
                db.commit()
            except:
                db.rollback()
                raise
        await exchange.close()

    db.close()


@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler(timezone=pytz.utc)
    scheduler.add_job(getCandleStickData, 'interval', minutes=1)
    scheduler.start()
    pass


@app.on_event("shutdown")
async def shutdown():
    pass


@app.post("/add-symbol/", response_model=SchemaSymbol)
def add_symbol(symbol: SchemaSymbol):
    db_symbol = ModelSymbol(name=symbol.name, exchange_id=symbol.exchange_id)
    db.add(db_symbol)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    return db_symbol


@app.post("/add-exchange/", response_model=SchemaExchange)
def add_exchange(exchange: SchemaExchange):
    db_exchange = ModelExchange(name=exchange.name)
    db.add(db_exchange)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    return db_exchange


@app.get("/symbols/")
def get_symbols():
    symbols = db.query(ModelSymbol).all()

    return symbols


@app.get("/exchanges/")
def get_exchanges():
    exchanges = db.query(ModelExchange).all()

    return exchanges


# add the timeframe and the symbol and the exchange
@app.get("/minuteBars/")
def get_minutes(symbol_id: int, timeframe: str):

    minutes = db.query(
        ModelMinuteBars).filter(ModelMinuteBars.symbol_id == symbol_id).all()

    df = pd.DataFrame([m.__dict__ for m in minutes])
    df.drop(['_sa_instance_state', 'symbol_id', 'id'],
            axis=1, inplace=True)
    kline = changeCandleTimeFrame(df, timeframe)

    return kline


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def authenticate_user(username: str, password: str):
    user = db.query(ModelUser).filter(ModelUser.username == username).first()

    if not user:
        return False
    if not user.verify_password(password):
        return False

    return user


@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        return {"error": "invalid credentials"}

    token = jwt.encode(
        {"username": user.username, "id": user.id}, JWT_SECRET)

    return {'access_token': token, 'token_type': 'bearer'}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = db.query(ModelUser).filter(
            ModelUser.id == payload.get('id')).first()
        print(user)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    return user


@app.post('/create-user', response_model=UserOut)
async def create_user(user: UserIn):
    user_obj = ModelUser(username=user.username,
                         password_hash=bcrypt.hash(user.password_hash))
    db.add(user_obj)
    try:
        db.commit()
    except:
        db.rollback()

        raise
    return {"username": user.username}


@app.get('/users/me', response_model=UserOut)
async def get_user(user: UserIn = Depends(get_current_user)):
    # print("this is username", user.username)
    return {"username": user.username}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
