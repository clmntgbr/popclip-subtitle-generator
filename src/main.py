import os
import re
import ffmpeg
import assemblyai as aai

from functools import partial
from concurrent.futures import ThreadPoolExecutor
from kombu import Queue
from flask import Flask
from celery import Celery
from datetime import timedelta

from src.config import Config
from src.s3_client import S3Client
from src.rabbitmq_client import RabbitMQClient
from src.file_client import FileClient
from src.converter import ProtobufConverter
from src.Protobuf.Message_pb2 import ClipStatus, Clip, SubtitleGeneratorMessage

app = Flask(__name__)
app.config.from_object(Config)
s3_client = S3Client(Config)
rmq_client = RabbitMQClient()
file_client = FileClient()

celery = Celery("tasks", broker=app.config["RABBITMQ_URL"])

celery.conf.update(
    {
        "task_serializer": "json",
        "accept_content": ["json"],
        "broker_connection_retry_on_startup": True,
        "task_routes": {
            "tasks.process_message": {"queue": app.config["RMQ_QUEUE_WRITE"]}
        },
        "task_queues": [
            Queue(
                app.config["RMQ_QUEUE_READ"], routing_key=app.config["RMQ_QUEUE_READ"]
            )
        ],
    }
)

@celery.task(name="tasks.process_message", queue=app.config["RMQ_QUEUE_READ"])
def process_message(message):
    clip: Clip = ProtobufConverter.json_to_protobuf(message)
    
    chunks = []

    try:
        for audio in clip.originalVideo.audios:
            chunks.append(audio)

        partialMultiprocess = partial(multiprocess, clip=clip)

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(partialMultiprocess, chunks))

        resultsSorted = sorted(results, key=extract_chunk_number)
        clip.originalVideo.subtitles.extend(resultsSorted)

        clip.status = ClipStatus.Name(
            ClipStatus.SUBTITLE_GENERATOR_COMPLETE
        )

        protobuf = SubtitleGeneratorMessage()
        protobuf.clip.CopyFrom(clip)

        rmq_client.send_message(protobuf, "App\\Protobuf\\SubtitleGeneratorMessage")
        return True
    except Exception:
        clip.status = ClipStatus.Name(
            ClipStatus.SUBTITLE_GENERATOR_ERROR
        )

        protobuf = SubtitleGeneratorMessage()
        protobuf.clip.CopyFrom(clip)

        if not rmq_client.send_message(protobuf, "App\\Protobuf\\SubtitleGeneratorMessage"):
            return False

def multiprocess(chunk: str, clip: Clip):
    key = f"{clip.userId}/{clip.id}/audios/{chunk}"
    tmpFilePath = f"/tmp/{chunk}"
    tmpSrtFilePath = os.path.splitext(tmpFilePath)[0] + ".srt"

    if not s3_client.download_file(key, tmpFilePath):
        raise Exception()

    if not generate_subtitle_assemblyAI(tmpFilePath, tmpSrtFilePath):
        raise Exception()

    key = f"{clip.userId}/{clip.id}/subtitles/{os.path.basename(tmpSrtFilePath)}"

    if not s3_client.upload_file(tmpSrtFilePath, key):
        raise Exception()

    return os.path.basename(tmpSrtFilePath)

def extract_chunk_number(item):
    match = re.search(r"_(\d+)\.srt$", item[0])
    return int(match.group(1)) if match else float("inf")

def ms_to_srt_time(ms):
    td = timedelta(milliseconds=ms)
    return f"{td.seconds // 3600:02}:{(td.seconds % 3600) // 60:02}:{td.seconds % 60:02},{td.microseconds // 1000:03}"

def generate_subtitle_assemblyAI(tmpFilePath: str, tmpSrtFilePath: str) -> bool:
    print("Uploading file for transcription...")

    aai.settings.api_key = Config.ASSEMBLY_AI_API_KEY
    config = aai.TranscriptionConfig(language_detection=True)
    transcriber = aai.Transcriber(config=config)

    transcript = transcriber.transcribe(tmpFilePath)
    words = transcript.words

    srtContent = ""
    subIndex = 1
    currentLine = []
    startTime = words[0].start

    for i, word in enumerate(words):
        currentLine.append(word.text)

        if len(currentLine) >= 6 or i == len(words) - 1:
            endTime = words[i].end

            mid_index = len(currentLine) // 2
            first_line = " ".join(currentLine[:mid_index])
            second_line = " ".join(currentLine[mid_index:])

            srtContent += f"{subIndex}\n"
            srtContent += f"{ms_to_srt_time(startTime)} --> {ms_to_srt_time(endTime)}\n"
            srtContent += f"{first_line}\n{second_line}\n\n"

            subIndex += 1
            currentLine = []
            if i < len(words) - 1:
                startTime = words[i + 1].start

    print("File successfully transcribed")

    with open(tmpSrtFilePath, "w", encoding="utf-8") as file:
        file.write(srtContent)

    print("SRT file successfully generated")
    return True