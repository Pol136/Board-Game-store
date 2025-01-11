from confluent_kafka import Consumer, KafkaError
from table_actions import add_user, delete_user_by_email, update_email_by_name
from fastapi import Request, Response
from string_operations import write_string_to_file

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumers_shop',
    'auto.offset.reset': 'earliest',
}

SESSION_COOKIE_NAME = "access_token"

consumer = Consumer(kafka_config)
topics = ['users_operations']
consumer.subscribe(topics)


def process_message(message):
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
