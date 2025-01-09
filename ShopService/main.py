from datetime import timedelta, datetime
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from token_actions import create_access_token, get_current_user
from models import User
from table_actions import (create_table, add_user, get_user_by_email, get_all_users,
                           authenticate_user)
from auth_router import router as auth_router

SECRET_KEY = "89C314947595C82FCA6B7EFC86FE8F2FFF4DE6A071A5489633AD73DBEDAF3324"
ALGORITHM = "HS256"

app = FastAPI()

app.include_router(auth_router)

user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/users", status_code = status.HTTP_200_OK)
async def get_users(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        return {"user": user}
        # try:
        #     return get_all_users()
        # except:
        #     raise HTTPException(status_code=400, detail="Users table does not exist")
