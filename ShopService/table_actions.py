import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from password_actions import hash_password, verify_password
from models import Base, User, Game, Order
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")


def create_table():
    inspector = inspect(engine)

    has_users_table = 'users' in inspector.get_table_names()
    has_game_table = 'games' in inspector.get_table_names()
    has_orders_table = 'orders' in inspector.get_table_names()

    if not has_users_table and not has_game_table and not has_orders_table:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            new_user = User(username='admin', email='admin@admin', role='admin')
            session.add(new_user)
            session.commit()


def add_user(username: str, email: str, role: str):
    with Session(engine) as session:
        new_user = User(username=username, email=email, role=role)
        session.add(new_user)
        session.commit()


def get_all_users():
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


def delete_user_by_email(email: str):
    with Session(engine) as session:
        user = session.query(User).filter(User.email ==email).first()
        if user:
            session.delete(user)
            session.commit()

def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()


def update_email(user_id: int, new_email: str):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.email = new_email
            session.commit()


def update_email_by_name(username: str, new_email: str):
    with Session(engine) as session:
        user = session.query(User).filter(User.username == username).first()
        if user:
            user.email = new_email
            session.commit()


def create_game(name: str, description: str, price: float):
    try:
        with Session(engine) as session:
            new_game = Game(name=name, description=description, price=price)
            session.add(new_game)
            session.commit()
            return {
                "id": new_game.id,
                "name": new_game.name,
                "description": new_game.description,
                "price": new_game.price
            }
    except SQLAlchemyError as e:
        print(f"Error creating game: {e}")
        return None


def update_game(game_id: int, name: str = None, description: str = None, price: float = None):
    try:
        with Session(engine) as session:
            game = session.query(Game).filter(Game.id == game_id).first()
            if game:
                if name is not None:
                    game.name = name
                if description is not None:
                    game.description = description
                if price is not None:
                    game.price = price
                session.commit()
                return {
                    "id": game.id,
                    "name": game.name,
                    "description": game.description,
                    "price": game.price
                }
            else:
                print(f"Game with ID {game_id} not found.")
                return None
    except SQLAlchemyError as e:
        print(f"Error updating game: {e}")
        return None


def delete_game(game_id: int):
    try:
        with Session(engine) as session:
            game = session.query(Game).filter(Game.id == game_id).first()
            if game:
                session.delete(game)
                session.commit()
                return True
            else:
                print(f"Game with ID {game_id} not found.")
                return False
    except SQLAlchemyError as e:
        print(f"Error deleting game: {e}")
        return False


def get_all_games():
    try:
        with Session(engine) as session:
            games = session.query(Game).all()
            if games:
                return [
                    {
                        "id": game.id,
                        "name": game.name,
                        "description": game.description,
                        "price": game.price
                    }
                    for game in games
                ]
            else:
                return []
    except SQLAlchemyError as e:
        print(f"Error getting all games: {e}")
        return None


def create_order(user_id: int, game_ids: list[int]) -> Dict | None:
    try:
        with Session(engine) as session:
            games = session.query(Game).filter(Game.id.in_(game_ids)).all()
            full_price = sum(game.price for game in games)
            new_order = Order(full_price=full_price, user_id=user_id, status="create")
            new_order.games.extend(games)
            session.add(new_order)
            session.commit()
            return _serialize_order(new_order)
    except SQLAlchemyError as e:
        print(f"Error creating order: {e}")
        return None


def delete_order(order_id: int) -> bool:
    try:
        with Session(engine) as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                session.delete(order)
                session.commit()
                return True
            else:
                print(f"Order with ID {order_id} not found.")
                return False
    except SQLAlchemyError as e:
        print(f"Error deleting order: {e}")
        return False


def get_user_by_order_id(order_id: int):
    try:
        with Session(engine) as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                user_id = order.user_id
                return get_user(user_id)
    except Exception as e:
        print(f"Error: {e}")
        return None


def update_order_status(order_id: int, status: str) -> Dict | None:
    try:
        with Session(engine) as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = status
                session.commit()
                return _serialize_order(order)
            else:
                print(f"Order with ID {order_id} not found.")
                return None
    except SQLAlchemyError as e:
        print(f"Error updating order status: {e}")
        return None



def get_all_orders() -> List[Dict] | None:
    try:
        with Session(engine) as session:
            orders = session.query(Order).all()
            if orders:
                return [_serialize_order(order) for order in orders]
            else:
                return []
    except SQLAlchemyError as e:
        print(f"Error getting all orders: {e}")
        return None


def get_order_by_id(order_id: int) -> Dict | None:
    try:
        with Session(engine) as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                return _serialize_order(order)
            else:
                print(f"Order with ID {order_id} not found.")
                return None
    except SQLAlchemyError as e:
        print(f"Error getting order by ID: {e}")
        return None


def _serialize_order(order: Order) -> Dict:
    return {
        "id": order.id,
        "full_price": order.full_price,
        "user_id": order.user_id,
        "status": order.status,
        "games": [
            {
                "id": game.id,
                "name": game.name,
                "description": game.description,
                "price": game.price
            }
            for game in order.games
        ]
    }