from send_email import send_email
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from table_actions import get_all_users, create_table, authenticate_user, add_user
from datetime import timedelta
from pydantic import BaseModel
from token_actions import create_access_token, get_user_if_admin

order_status = {'create': 'Ваш заказ создан',
                'delivered': 'Ваш заказ доставлен в магазин',
                'received': 'Заказ получен\nСпасибо за покупку!',
                'cancelled': 'Ваш заказ был отменен'}

app = FastAPI()

create_table()
# add_user('polina', 'polina20050326@gmail.com', 'user', '12345')

admin_dependency = Annotated[dict, Depends(get_user_if_admin)]

class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token = create_access_token(user.id, user.username, user.email, user.role, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}


@app.get("/users")
async def get_users(admin: admin_dependency):
    if admin is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        return get_all_users()


@app.post("/selective_mailing")
async def mailing(admin: admin_dependency, subject: str, body: str, to_email: list):
    if admin is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        send_email(subject, body, to_email)
        return f"Email was send to {to_email}"


@app.post("/mail_to_all_users")
async def mailing_users(admin: admin_dependency, subject: str, body: str):
    if admin is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    else:
        to_email = []
        users = get_all_users()
        for user in users:
            to_email.append(user.email)
        send_email(subject, body, to_email)
        return "All users was emailed"
