FROM python:3.9-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
