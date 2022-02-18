import datetime
import time

import ccxt.async_support as ccxt
import pandas as pd
from sqlalchemy.orm.session import Session

from .bybitCredentials import APIkey, APIsecret
from .db_conf import db_session
from .models.models import Exchange as Exchange
from .models.models import MinuteBars as MinuteBars
from .models.models import Symbol as Symbol
from .schema.schema import SchemaExchange

db: Session = db_session.session_factory()


def getExchangeObject(exchange: SchemaExchange) -> ccxt.Exchange:
    if exchange.name == "bybit":
        return ccxt.bybit({
            "apiKey": APIkey,
            "secret": APIsecret
        })


def changeCandleTimeFrame(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    ohlc = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    }
    df = df.resample(timeframe, on='date').apply(ohlc)
    # the available timeframes: https://stackoverflow.com/questions/17001389/pandas-resample-documentation
    df = df.reset_index()
    df.rename(columns={"date": "time"}, inplace=True)

    df["time"] = (df['time'] - pd.Timestamp("1970-01-01"))//pd.Timedelta('1s')

    print(df.head())

    # df = df.fillna('')
    df = df.drop(df[df.volume == 0].index)
    df = df.to_dict(orient='records')
    return df


async def getCandleStickData():
    exchanges = db.query(Exchange).all()
    for exchange in exchanges:
        exchange_id = exchange.id
        exchange = getExchangeObject(exchange)

        symbols = db.query(Symbol).filter(
            Symbol.exchange_id == exchange_id)
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
                MinuteBars).filter(MinuteBars.symbol_id == symbol.id).order_by(MinuteBars.id.desc()).first()

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
                        kline = MinuteBars(
                            date=dfTime, open=open, high=high, low=low, close=close, volume=volume, symbol_id=symbol.id)
                        db.add(kline)
                        insertRest = True
                else:
                    open = df['open'].loc[each_line]
                    high = df['high'].loc[each_line]
                    low = df['low'].loc[each_line]
                    close = df['close'].loc[each_line]
                    volume = df['volume'].loc[each_line]
                    kline = MinuteBars(
                        date=dfTime, open=open, high=high, low=low, close=close, volume=volume, symbol_id=symbol.id)
                    db.add(kline)

            try:
                db.commit()
            except:
                db.rollback()
                raise
        await exchange.close()

    db.close()
