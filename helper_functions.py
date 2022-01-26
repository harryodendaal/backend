from schema import Exchange as SchemaExchange, MinuteBars
import ccxt.async_support as ccxt
from bybitCredentials import APIkey, APIsecret
import pandas as pd
import datetime
import time


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
    df = df.reset_index()
    df.rename(columns={"date": "time"}, inplace=True)

    df["time"] = (df['time'] - pd.Timestamp("1970-01-01"))//pd.Timedelta('1s')

    print(df.head())

    # df = df.fillna('')
    df = df.drop(df[df.volume == 0].index)
    df = df.to_dict(orient='records')
    return df
