from send_email import send_email
from fastapi import FastAPI
from table_actions import get_all_users, create_table

order_status = {'create': 'Ваш заказ создан',
                'delivered': 'Ваш заказ доставлен в магазин',
                'received': 'Заказ получен\nСпасибо за покупку!',
                'cancelled': 'Ваш заказ был отменен'}

app = FastAPI()

create_table()

@app.post("/selective_mailing")
async def mailing(subject: str, body: str, to_email: list):
    send_email(subject, body, to_email)


@app.post("/mail_to_all_users")
async def mailing_users(subject: str, body: str):
    to_email = []
    users = get_all_users()
    for user in users:
        to_email.append(user.email)
    send_email(subject, body, to_email)
