FROM python:alpine

WORKDIR /app
COPY requirements.txt .
RUN ["pip", "install", "-r", "/app/requirements.txt" ]

COPY src .
CMD ["python3", "/app/main.py"]
