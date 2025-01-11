from fastapi import APIRouter, HTTPException, Depends, status, Response, Cookie, Request
from table_actions import create_table, get_user_by_email, add_user, authenticate_user
from token_actions import create_access_token
from pydantic import BaseModel
from datetime import timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from kafka_producer import send_message


class Token(BaseModel):
    access_token: str
    token_type: str


SESSION_COOKIE_NAME = "access_token"
router = APIRouter(prefix='/users', tags=['users'])


@router.post("/register")
async def create_user(username: str, email: EmailStr, password: str):
    create_table()
    try_find_user = get_user_by_email(email)
    print(try_find_user)
    if not try_find_user is None:
        raise HTTPException(status_code=400, detail="Email is already registered")
    else:
        add_user(username, email, password, 'user')
        send_message('users_operations', f"add_user {username} {email} user")
        return "complete"


@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.id, user.username, user.email, user.role, timedelta(minutes=30))
    response.set_cookie(
        key=SESSION_COOKIE_NAME, value=token, httponly=True, samesite="lax"  # Устанавливаем cookie
    )
    send_message('users_operations', f"logged_in {token}")
    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/get_cookie")
async def get_cookie(request: Request):
    try:
        token_info = request.cookies.get(SESSION_COOKIE_NAME)
        return token_info
    except Exception as e:
        return str(e)
