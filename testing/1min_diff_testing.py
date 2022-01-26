
from email.mime import base
import pandas as pd
import time
import json
import asyncio
import ccxt.async_support as ccxt
import math

from sqlalchemy import BIGINT

APIkey = "XxnvexcTFwnf7Rj1fw"
APIsecret = "9QMu3OQ94Vr1gPoTSUKgq8ke4m20wc9uDsl0"

exchange = ccxt.bybit({
    "apiKey": APIkey,
    "secret": APIsecret
})
timeframe = 15
data = pd.read_csv(
    r'/home/penguin/documents/trading_app/backend/testing/data-1642928389037.csv')


data['date'] = pd.to_datetime(data['date'], unit='ms')


ohlc = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum"
}

df = data.resample('15min', on='date').apply(ohlc)
df = df.reset_index()
# jsonifiedData = df.apply(lambda x: x.to_json(), axis=1)
val = (df.to_dict(orient="records"))
print(val[0])
