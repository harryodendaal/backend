
import pandas as pd
import time
import ccxt
Name = "trading_website"
APIkey = "XxnvexcTFwnf7Rj1fw"
APIsecret = "9QMu3OQ94Vr1gPoTSUKgq8ke4m20wc9uDsl0"
Permission = "Contracts - Orders Positions , SPOT - Trade , Wallet - Account Transfer Subaccount Transfer  "

exchange = ccxt.bybit({
    "apiKey": APIkey,
    "secret": APIsecret
})

data = exchange.fetch_ohlcv(
    "BIT/USDT", '1d', limit=100)
df = pd.DataFrame(data)

col_names = ['time', 'open', 'high', 'low', 'close', 'volume']

df.columns = col_names

for col in col_names:
    df[col] = df[col].astype(float)


for line in df.index:
    print(df['open'].loc[line])
