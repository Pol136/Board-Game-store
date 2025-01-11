from confluent_kafka import Producer

kafka_config = {
    "bootstrap.servers": "localhost:9092"
}

producer = Producer(kafka_config)


def send_message(topic, value):
    try:
        producer.produce(topic, value=value)
        producer.flush()
        print(f"status Message sent {value}")
    except Exception as e:
        print(str(e))