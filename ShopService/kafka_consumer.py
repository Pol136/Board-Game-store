from confluent_kafka import Consumer, KafkaError
from table_actions import add_user, delete_user_by_email, update_email_by_name

kafka_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumers',
    'auto.offset.reset': 'earliest',
}

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
