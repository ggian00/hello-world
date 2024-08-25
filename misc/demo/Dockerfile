FROM python:3.12-bookworm

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y firefox-esr && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir .

CMD ["python", "demo/app.py"]

