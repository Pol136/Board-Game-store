import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from password_actions import hash_password, verify_password
from models import Base, User

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")


def create_table():
    """
    Создание таблиц (если их еще нет в базе данных)
    """
    inspector = inspect(engine)

    has_users_table = 'users' in inspector.get_table_names()

    if not has_users_table:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            new_user = User(username='admin', email='admin@admin', password=hash_password('admin'), role='admin')
            session.add(new_user)
            session.commit()


def add_user(username: str, email: str, password: str, role: str):
    """
    Добавление пользователя в таблицу пользователей
    """
    with Session(engine) as session:
        new_user = User(username=username, email=email, password=hash_password(password), role=role)
        session.add(new_user)
        session.commit()


def get_all_users():
    """
    Извлекает информацию о всех пользователях
    """
    with Session(engine) as session:
        users = session.query(User).all()
        return users


def get_user(id: int):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == id).first()
        if user:
            return user
        else:
            return None


def get_user_by_email(email: str):
    """
    Ищет пользователя по email
    """
    with Session(engine) as session:
        user = session.query(User).filter(User.email == email).first()
        if user:
            return user
        else:
            return None


def authenticate_user(username: str, password: str):
    with Session(engine) as session:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user


def update_email(user_id: int, new_email: str):
    """
    Обновляет email ользователя
    """
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.email = new_email
            session.commit()


def delete_user(user_id: int):
    """
    Удаляет пользователя по id
    """
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
