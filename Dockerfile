FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY .env .env

ENV PYTHONPATH=/app

CMD ["gunicorn", "--bind", "0.0.0.0:8899", "src.index:app"]