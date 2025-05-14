import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    RMQ_QUEUE_WRITE = os.getenv("RMQ_QUEUE_WRITE")
    RMQ_QUEUE_READ = os.getenv("RMQ_QUEUE_READ")

    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    S3_ENDPOINT = os.getenv("S3_ENDPOINT")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    S3_REGION = os.getenv("S3_REGION")

    ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")
