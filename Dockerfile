FROM python:alpine

RUN ["apk", "add", "gcc", "musl-dev", "libffi-dev", "openssl-dev"]

WORKDIR /app
COPY requirements.txt .
RUN ["pip", "install", "-r", "/app/requirements.txt" ]

COPY src .
CMD ["python3", "/app/main.py"]
