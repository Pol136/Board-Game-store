from confluent_kafka import Consumer, KafkaError
from send_email import send_email
from string_operations import write_string_to_file
from table_actions import add_user, delete_user_by_email, update_email_by_name

order_status = {'create': 'Ваш заказ создан',
                'delivered': 'Ваш заказ доставлен в магазин',
                'received': 'Заказ получен\nСпасибо за покупку!',
                'cancelled': 'Ваш заказ был отменен'}

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumers_not',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(kafka_config)
topics = ['orders_operations', 'users_operations']
consumer.subscribe(topics)


def process_message(message):
    if message.topic == 'users_operations':
        user_info = message.value().decode('utf-8').split(' ')
        if user_info[0] == 'add_user':
            add_user(user_info[1], user_info[2], user_info[3])
        elif user_info[0] == 'delete_user':
            delete_user_by_email(user_info[2])
        elif user_info[0] == 'update_user_email':
            update_email_by_name(user_info[1], user_info[2])
        elif user_info[0] == 'logged_in':
            print(user_info[1])
            write_string_to_file('token.txt', user_info[1])
        elif user_info[0] == 'logged_out':
            write_string_to_file('token.txt', "")
    else:
        order_info = message.value().decode('utf-8').split(' ')
        text = f"Здравствуйте, {order_info[1]} {order_status[order_info[0]]}"
        send_email("Статус вашего заказа изменен", text, order_info[2])


def consume_kafka():
    try:
        while True:
            msg = consumer.poll(0.1)

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
