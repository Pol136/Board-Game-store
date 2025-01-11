from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status, Request
from token_actions import create_access_token, get_current_user, get_user_if_admin
from auth_router import router as auth_router
from table_actions import delete_user, get_all_users, update_email, get_user, create_table
from pydantic import EmailStr
import json
from kafka_producer import send_message

create_table()

app = FastAPI()

app.include_router(auth_router)

user_dependency = Annotated[dict, Depends(get_current_user)]
admin_dependency = Annotated[dict, Depends(get_user_if_admin)]


@app.post("/update_user_email", status_code=status.HTTP_200_OK)
async def update_user_info(user: user_dependency, request: Request, new_email: EmailStr):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        try:
            update_email(user.get('user_id'), new_email)
            user_to_update = get_user(user.get('user_id'))
            send_message('users_operations', f"update_user_email {user_to_update.username} {user_to_update.email} user")
            return get_user(user.get('user_id'))
        except:
            raise HTTPException(status_code=400, detail="Couldn't update user information")


@app.get("/users", status_code=status.HTTP_200_OK)
async def get_users(user_session: dict = Depends(get_current_user)):
    # if admin is None:
    #     raise HTTPException(status_code=401, detail="Authentication Failed")
    # else:
    try:
        return get_all_users()
    except:
        raise HTTPException(status_code=400, detail="Users table does not exist")


@app.delete("/delete_user", status_code=status.HTTP_200_OK)
async def delete_user_by_id(admin: admin_dependency, user_id: int, request: Request):
    if admin is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        try:
            user_to_del = get_user(user_id)
            send_message('users_operations', f"delete_user {user_to_del.username} {user_to_del.email} user")
            delete_user(user_id)
            return f"User {user_id} has been deleted"
        except:
            raise HTTPException(status_code=400, detail="There is no user with this id")
