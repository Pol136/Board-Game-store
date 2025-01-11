from confluent_kafka import Consumer, KafkaError
from send_email import send_email

order_status = {'create': 'Ваш заказ создан',
                'delivered': 'Ваш заказ доставлен в магазин',
                'received': 'Заказ получен\nСпасибо за покупку!',
                'cancelled': 'Ваш заказ был отменен'}

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumers',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(kafka_config)
topics = ['orders_operations']
consumer.subscribe(topics)


def process_message(message):
    order_info = message.value().decode('utf-8').split(' ')
    text = f"Здравствуйте, {order_info[1]}\n{order_status[order_info[0]]}"
    send_email("Статус вашего заказа изменен", text, order_info[2])


def consume_kafka():
    consumer.subscribe(topics)
    try:
        while True:
            msg = consumer.poll(0.001)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    break
            process_message(msg)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
