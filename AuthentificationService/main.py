from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status, Request
from starlette.responses import Response

from token_actions import create_access_token, get_current_user, get_user_if_admin
from auth_router import router as auth_router
from table_actions import delete_user, get_all_users, update_email, get_user, create_table
from pydantic import EmailStr
import json
from kafka_producer import send_message

SESSION_COOKIE_NAME = "access_token"
create_table()

app = FastAPI()

app.include_router(auth_router)


# user_dependency = Annotated[dict, Depends(get_current_user)]
# admin_dependency = Annotated[dict, Depends(get_user_if_admin)]


@app.post("/update_user_email", status_code=status.HTTP_200_OK)
async def update_user_info(request: Request, new_email: EmailStr):
    user = get_current_user(request=request)
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
async def get_users(request: Request):
    user = get_current_user(request=request)
    if user and user['role'] == 'admin':
        try:
            return get_all_users()
        except:
            raise HTTPException(status_code=400, detail="Users table does not exist")
    else:
        raise HTTPException(status_code=401, detail="Authentication Failed")


@app.delete("/delete_user", status_code=status.HTTP_200_OK)
async def delete_user_by_id(user_id: int, request: Request):
    user = get_current_user(request=request)
    if user and user['role'] == 'admin':
        try:
            user_to_del = get_user(user_id)
            send_message('users_operations', f"delete_user {user_to_del.username} {user_to_del.email} user")
            delete_user(user_id)
            return f"User {user_id} has been deleted"
        except:
            raise HTTPException(status_code=400, detail="There is no user with this id")
    else:
        raise HTTPException(status_code=401, detail="Authentication Failed")


@app.delete("/logout", status_code=status.HTTP_200_OK)
async def logout_user(request: Request, response: Response):
    user = get_current_user(request=request)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        response.set_cookie(
            key=SESSION_COOKIE_NAME, value='', httponly=True, samesite="lax"
        )
        return "Your token was deleted"
