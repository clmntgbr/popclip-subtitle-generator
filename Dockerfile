FROM python:3.10-slim as upstream

FROM upstream AS base

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install watchdog flask-debug

COPY . .

RUN mkdir -p /tmp && chmod 777 /tmp

FROM base AS dev

ENV FLASK_APP=src/main.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

CMD ["flask", "--app", "src/main.py", "run", "--host=0.0.0.0", "--port=5000", "--reload"]

FROM base AS prod

ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=1

CMD ["gunicorn", "--workers=4", "--bind", "0.0.0.0:5000", "src.main:app"]