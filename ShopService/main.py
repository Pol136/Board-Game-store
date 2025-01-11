from fastapi import FastAPI
from games_apis import router as games_router
from orders_apis import router as orders_router
from table_actions import add_user, create_table
import threading
from kafka_consumer import consume_kafka

create_table()

# add_user('polina', 'polina20050326@gmail.com', 'user')

app = FastAPI()
app.include_router(games_router)
app.include_router(orders_router)


@app.on_event("startup")
async def startup_event():
    threading.Thread(target=consume_kafka, daemon=True).start()
