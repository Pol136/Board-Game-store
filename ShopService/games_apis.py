from table_actions import create_table, create_game, update_game, delete_game, get_all_games
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from typing import Annotated, List
from pydantic import BaseModel

router = APIRouter(prefix='/games', tags=['games'])


# Модель для создания игры
class GameCreate(BaseModel):
    name: str
    description: str
    price: float


# Модель для обновления игры
class GameUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None


# Модель для вывода игры
class GameResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float


@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_new_game(game: GameCreate):
    new_game = create_game(name=game.name, description=game.description, price=game.price)
    if new_game:
        return new_game
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create game")


@router.put("/{game_id}", response_model=GameResponse)
async def update_existing_game(game_id: int, game: GameUpdate):
    updated_game = update_game(game_id=game_id, name=game.name, description=game.description, price=game.price)
    if updated_game:
        return updated_game
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_game(game_id: int):
    deleted = delete_game(game_id=game_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")


@router.get("/", response_model=List[GameResponse])
async def get_all_existing_games():
    games = get_all_games()
    if games:
        return games
    else:
        return []