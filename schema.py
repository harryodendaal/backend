from pydantic import BaseModel


class MinuteBars(BaseModel):
    date: int  # will this be a problem 2038?
    open: float
    high: float
    low: float
    close: float
    volume: int
    symbol_id: int

    class Config:
        orm_mode = True


class Symbol(BaseModel):
    name: str
    exchange_id: int

    class Config:
        orm_mode = True


class Exchange(BaseModel):
    name: str

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    username: str
    password_hash: str


class UserOut(BaseModel):
    username: str
