FROM ubuntu:bionic
LABEL maintainer="Sudipto Chandra"

WORKDIR /usr/src/app

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

RUN apt-get update

RUN apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
  && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

RUN apt-get update

RUN apt-get install -y python3-pip python3-dev

RUN pip3 install --upgrade pip

RUN pip3 install lightnovel-crawler

CMD [ "lncrawl" ]
