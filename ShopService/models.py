from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import event
from sqlalchemy.engine import Engine

Base = declarative_base()


class User(Base):
    """
    Класс Пользователь
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    orders = relationship("Order", back_populates="user")


class Game(Base):
    """
    Класс Игры
    """
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)


order_game_association = Table(
    'order_game_association', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('game_id', Integer, ForeignKey('games.id'), primary_key=True)
)


class Order(Base):
    """
    Класс Заказ
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String)
    user = relationship("User", back_populates="orders")
    games = relationship("Game", secondary=order_game_association)
