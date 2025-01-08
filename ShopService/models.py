from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """
    Класс Пользователь
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, unique=False, nullable=False)
    password = Column(String, nullable=False)
