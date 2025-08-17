HEAD
FROM python:3.9

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
=======
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn

# Render requires listening on $PORT
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

dabb2350b34adb255eac2944eba0b925cd441175
