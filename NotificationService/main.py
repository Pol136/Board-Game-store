from send_email import send_email
from fastapi import FastAPI, HTTPException, status, Depends, Request
from table_actions import get_all_users, create_table, authenticate_user, add_user
from token_actions import create_access_token, get_current_user
import threading
from kafka_consumer import consume_kafka
from string_operations import read_string_from_file

app = FastAPI()

create_table()
# add_user('polina', 'polina20050326@gmail.com', 'user')
# admin_dependency = Annotated[dict, Depends(get_user_if_admin)]


@app.on_event("startup")
async def startup_event():
    threading.Thread(target=consume_kafka, daemon=True).start()


# @app.post("/selective_mailing")
# async def mailing(subject: str, body: str, to_email: list):
#     token = read_string_from_file('token.txt')
#     user = get_current_user(token)
#     if user and user['role'] == 'admin':
#         send_email(subject, body, to_email)
#         return f"Email was send to {to_email}"
#     else:
#         raise HTTPException(status_code=401, detail="Authentication Failed")


@app.post("/mail_to_all_users")
async def mailing_users(subject: str, body: str):
    token = read_string_from_file('token.txt')
    user = get_current_user(token)
    if user and user['role'] == 'admin':
        to_email = []
        users = get_all_users()
        for user in users:
            to_email.append(user.email)
        send_email(subject, body, to_email)
        return "All users was emailed"
    else:
        raise HTTPException(status_code=401, detail="Authentication Failed")
