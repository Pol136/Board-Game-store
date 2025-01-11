from send_email import send_email
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from table_actions import get_all_users, create_table, authenticate_user, add_user
from datetime import timedelta
from pydantic import BaseModel
from token_actions import create_access_token, get_user_if_admin
import threading
from kafka_consumer import consume_kafka

app = FastAPI()

create_table()
# add_user('polina', 'polina20050326@gmail.com', 'user', '12345')

admin_dependency = Annotated[dict, Depends(get_user_if_admin)]


@app.on_event("startup")
async def startup_event():
    threading.Thread(target=consume_kafka, daemon=True).start()


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
