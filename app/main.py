# other schedulers are available

import pytz
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.hash import bcrypt
from sqlalchemy.orm.session import Session

from .db_conf import db_session
from .helper_functions import getCandleStickData
from .routers import authorization, exchanges, kline, symbols


db: Session = db_session.session_factory()
# load_dotenv(".env")


app = FastAPI()
app.include_router(authorization.router)
app.include_router(exchanges.router)
app.include_router(kline.router)
app.include_router(symbols.router)

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


@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler(timezone=pytz.utc)
    scheduler.add_job(getCandleStickData, 'interval', minutes=1)
    scheduler.start()
    print('hello')
    pass


@app.on_event("shutdown")
async def shutdown():
    pass


# add the timeframe and the symbol and the exchange


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
