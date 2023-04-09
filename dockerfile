FROM python:3.8.16-alpine3.17

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /app

CMD ["gunicorn", "main:app" , "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
