from fastapi import APIRouter, HTTPException, Depends, status
from table_actions import create_table, get_user_by_email, add_user, authenticate_user
from token_actions import create_access_token
from pydantic import BaseModel
from datetime import timedelta
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

class Token(BaseModel):
    access_token: str
    token_type: str

router = APIRouter(prefix='/users', tags=['users'])

@router.post("/register")
async def create_user(username: str, email: str, password: str):
    create_table()
    try_find_user = get_user_by_email(email)
    print(try_find_user)
    if not try_find_user is None:
        raise HTTPException(status_code=400, detail="Email is already registered")
    else:
        add_user(username, email, password, 'user')
        return "complete"


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token = create_access_token(user.id, user.username, user.email, user.role, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}