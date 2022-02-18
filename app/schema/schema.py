from pydantic import BaseModel


class SchemaMinuteBars(BaseModel):
    date: int  # will this be a problem 2038?
    open: float
    high: float
    low: float
    close: float
    volume: int
    symbol_id: int

    class Config:
        orm_mode = True


class SchemaSymbol(BaseModel):
    name: str
    exchange_id: int

    class Config:
        orm_mode = True


class SchemaExchange(BaseModel):
    name: str

    class Config:
        orm_mode = True


class SchemaUserIn(BaseModel):
    username: str
    password_hash: str


class SchemaUserOut(BaseModel):
    username: str
