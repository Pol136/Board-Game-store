from fastapi import FastAPI, HTTPException

from models import User
from table_actions import (create_table, add_user, get_user_by_email, get_all_users)

SECRET_KEY = "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3"
ALGORITHM = "HS256"

app = FastAPI()

@app.post("/register")
async def create_user(username:str, email:str, password:str):
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
        raise  HTTPException(status_code=400, detail="Users table does not exist")