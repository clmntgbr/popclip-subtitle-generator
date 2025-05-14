import pika
import json
from src.config import Config
from google.protobuf.json_format import MessageToJson


class RabbitMQClient:
    @staticmethod
    def send_message(mediaPod, type: str) -> bool:
        try:
            message = {
                "task": "tasks.process_message",
                "args": [MessageToJson(mediaPod)],
                "queue": Config.RMQ_QUEUE_WRITE,
            }

            parameters = pika.URLParameters(Config.RABBITMQ_URL)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.basic_publish(
                exchange="microservices",
                routing_key=Config.RMQ_QUEUE_WRITE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                    headers={"type": type},
                ),
            )

            return True
        except Exception as e:
            print(e)
