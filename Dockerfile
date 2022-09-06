FROM python:alpine AS build

RUN ["apk", "add", "gcc", "musl-dev", "libffi-dev", "openssl-dev", "libxml2-dev", "libxslt-dev", "rust", "cargo"]

WORKDIR /build
COPY requirements.txt .
RUN python3 -m venv /app/env && source /app/env/bin/activate && python3 -m pip install -r /build/requirements.txt


FROM python:alpine

WORKDIR /app
COPY --from=build /app ./
COPY src .
ENV PATH="/app/env/bin:$PATH"
ENTRYPOINT ["python3", "/app/main.py"]
