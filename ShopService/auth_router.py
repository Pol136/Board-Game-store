from fastapi import APIRouter, HTTPException, Depends, status
from table_actions import create_table, get_user_by_email, add_user, authenticate_user
# from token_actions import create_access_token
from pydantic import BaseModel
from datetime import timedelta, datetime
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import jwt

SECRET_KEY = "89C314947595C82FCA6B7EFC86FE8F2FFF4DE6A071A5489633AD73DBEDAF3324"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl = 'users/token')

def create_access_token(id: int, username: str, email: str, role: str, expires_delta: timedelta):
    encode = {'name': username, 'id': id, 'email': email, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
        username: str = payload.get('name')
        user_id: int = payload.get('id')
        if username is None and user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate user")
        else:
            return {'username': username, 'user_id': user_id}
    except:
        raise HTTPException(status_code=401, detail="Could not validate user")

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