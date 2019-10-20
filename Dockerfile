FROM python:3.6-alpine
LABEL maintainer="Sudipto Chandra"

WORKDIR /usr/src/app

RUN apk add --no-cache g++ gcc cairo-dev jpeg-dev libxslt-dev openssl-dev
RUN pip install --no-cache-dir -U lightnovel-crawler

COPY mycreds.txt mycreds.txt

ENV SSL_CERT_DIR=/etc/ssl/certs

ARG bot
ENV BOT=${bot}

ARG log_level=INFO
ENV LOG_LEVEL=${log_level}

ARG telegram_token
ENV TELEGRAM_TOKEN=${telegram_token}

ARG discord_token
ENV DISCORD_TOKEN=${discord_token}

ARG discord_signal_char=!
ENV DISCORD_SIGNAL_CHAR=${discord_signal_char}

CMD [ "lncrawl" ]
