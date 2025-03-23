FROM python:3.9-slim

WORKDIR /app

COPY client.py .


RUN pip install --upgrade pip && \
    pip install --no-cache-dir pickle-mixin packet

CMD ["python", "client.py"]