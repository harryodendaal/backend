from passlib.hash import bcrypt
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Numeric, BIGINT, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# BIT, ETH, BTC to start with
# exchange, symbols, data


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    password_hash = Column(String(128))

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


class MinuteBars(Base):
    __tablename__ = "minutebars"
    id = Column(Integer, primary_key=True)
    date = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BIGINT)
    symbol_id = Column(Integer, ForeignKey('symbol.id'))
    symbol = relationship("Symbol")


class Symbol(Base):
    __tablename__ = "symbol"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    exchange_id = Column(Integer, ForeignKey('exchange.id'))
    exchange = relationship("Exchange")


class Exchange(Base):
    __tablename__ = "exchange"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
