FROM python:3.9.6-slim

RUN apt update && apt install -y libpq-dev gcc

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create the app directory - and switch to it
RUN mkdir -p /app
WORKDIR /app

# install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

# copy project
COPY . /app/

# expose port 8000
EXPOSE 8000

CMD ["python3", "src/bot.py"]