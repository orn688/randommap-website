FROM python:3.6.1-alpine

ENV FLASK_PORT 5000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV APP_DIR /app

RUN mkdir $APP_DIR
WORKDIR $APP_DIR

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN source .env

EXPOSE $FLASK_PORT

CMD ["python", "main.py"]
