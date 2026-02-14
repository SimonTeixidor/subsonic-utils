FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sync_and_cleanup.py .

ENTRYPOINT ["python", "sync_and_cleanup.py"]
