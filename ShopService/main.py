from datetime import timedelta, datetime
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from token_actions import  create_access_token
from models import User
from table_actions import (create_table, add_user, get_user_by_email, get_all_users,
                           authenticate_user)

SECRET_KEY = "89C314947595C82FCA6B7EFC86FE8F2FFF4DE6A071A5489633AD73DBEDAF3324"
ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


app = FastAPI()


@app.post("/register")
async def create_user(username: str, email: str, password: str):
    create_table()
    try_find_user = get_user_by_email(email)
    print(try_find_user)
    if not try_find_user is None:
        raise HTTPException(status_code=400, detail="Email is already registered")
    else:
        add_user(username, email, password, 'user')
        return "complete"


@app.get("/users")
async def get_users():
    try:
        return get_all_users()
    except:
        raise HTTPException(status_code=400, detail="Users table does not exist")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token = create_access_token(user.id, user.username, user.email, user.role, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}
