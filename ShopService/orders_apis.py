from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from typing import Annotated, List
from pydantic import BaseModel
from kafka_producer import send_message
from table_actions import create_order, delete_order, update_order_status, get_all_orders, get_order_by_id, get_user

router = APIRouter(prefix='/orders', tags=['orders'])


# Модель для вывода данных игры в заказе
class GameInOrderResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float


# Модель для создания заказа (full_price больше не требуется)
class OrderCreate(BaseModel):
    game_ids: list[int]


# Модель для обновления заказа
class OrderUpdate(BaseModel):
    status: str


# Модель для вывода данных заказа
class OrderResponse(BaseModel):
    id: int
    full_price: float
    user_id: int
    status: str
    games: List[GameInOrderResponse]


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(user_id: int, order: OrderCreate):
    new_order = create_order(user_id=user_id, game_ids=order.game_ids)
    if new_order:
        send_message('orders_operations', f"create {get_user(user_id).username} {get_user(user_id).email}")
        return new_order
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_order(order_id: int):
    deleted = delete_order(order_id=order_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


@router.put("/{order_id}", response_model=OrderResponse)
async def update_existing_order(order_id: int, order: OrderUpdate):
    updated_order = update_order_status(order_id=order_id, status=order.status)
    if updated_order:
        return updated_order
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


@router.get("/", response_model=List[OrderResponse])
async def get_all_existing_orders():
    orders = get_all_orders()
    if orders:
        return orders
    else:
        return []


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id_handler(order_id: int):
    order = get_order_by_id(order_id=order_id)
    if order:
        return order
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
