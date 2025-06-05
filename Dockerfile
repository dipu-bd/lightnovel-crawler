##
# Setup Runner
##
FROM python:3.10-slim-bookworm as runner

# Install general dependencies
RUN apt-get update -yq \
    && apt-get install -yq \
    wget tar xz-utils make cmake g++ libffi-dev libegl1 libopengl0 libxcb-cursor0 \
    libnss3 libgl1-mesa-glx libxcomposite1 libxrandr2 libxi6 fontconfig \
    libxkbcommon-x11-0 libxtst6 libxkbfile1 libxcomposite-dev libxdamage-dev \
    && apt-get clean autoclean \
    && apt-get autoremove -yq \
    && rm -rf /var/lib/apt/lists/*

# Install calibre
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin \
    && ln -s /opt/calibre/ebook-convert /usr/local/bin/ebook-convert

# Add app user
RUN useradd -ms /bin/bash lncrawl
USER lncrawl

# Update pip
RUN python -m pip install -U pip

##
# Web assets builder
##
FROM node:alpine AS node

WORKDIR /app/lncrawl-web
COPY lncrawl-web/package.json package.json
COPY lncrawl-web/yarn.lock yarn.lock
RUN yarn

RUN mkdir -p ../lncrawl
COPY lncrawl-web .
RUN yarn build

##
# Application
##
FROM runner

WORKDIR /app

# Install requirements
COPY --chown=lncrawl:lncrawl requirements.txt .
RUN pip install -r requirements.txt

# Copy sources
COPY .env .env
COPY sources sources
COPY lncrawl lncrawl

# Copy web assets
COPY --from=node --chown=lncrawl:lncrawl /app/lncrawl/bots/server/web lncrawl/bots/server/web

# Copy web assets
ENV OUTPUT_PATH=/home/lncrawl/output
RUN mkdir -p $OUTPUT_PATH

ENTRYPOINT [ "python", "-m", "lncrawl" ]
