from kafka import KafkaProducer, KafkaConsumer
import json

def send_kafka_message(topic, value):
    producer = KafkaProducer(
        bootstrap_servers='kafka:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(topic, value=value)
    producer.flush() 
    producer.close()

def consume_kafka_message(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='kafka:29092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    for message in consumer:
        consumer.close()
        return message.value
    