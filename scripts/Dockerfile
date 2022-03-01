FROM python:3.9.10-slim-buster

RUN apt-get update -yq \
    && apt-get install -yq \
    wget tar xz-utils make cmake g++ libffi-dev \
    libnss3 libgl1-mesa-glx libxcomposite1 libxrandr2 libxi6 fontconfig \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean autoclean \
    && apt-get autoremove -yq

RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin

RUN useradd -ms /bin/bash appuser
USER appuser

WORKDIR /home/appuser/app

RUN export PATH="/home/appuser/.local/bin:$PATH"
RUN pip install -U pip wheel

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY lncrawl lncrawl
COPY sources sources

USER root
RUN chown -R appuser:appuser /home/appuser/app
USER appuser

ENTRYPOINT [ "python", "-m", "lncrawl" ]
