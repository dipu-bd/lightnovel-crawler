FROM python:3.10-slim-bookworm

USER root
# Install general dependencies
RUN apt-get update -yq \
    && apt-get install -yq \
    wget tar xz-utils make cmake g++ libffi-dev libegl1 libopengl0 libxcb-cursor0 \
    libnss3 libgl1-mesa-glx libxcomposite1 libxrandr2 libxi6 fontconfig \
    libxkbcommon-x11-0 libxtst6 libxkbfile1 libxcomposite-dev libxdamage-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean autoclean \
    && apt-get autoremove -yq

# Install calibre
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin \
    && ln -s /opt/calibre/ebook-convert /usr/local/bin/ebook-convert

# Add app user
RUN useradd -ms /bin/bash lncrawl
USER lncrawl

# Install global requirements
RUN alias python=python3
RUN alias pip=pip3
RUN export PATH="/home/lncrawl/.local/bin:$PATH"
RUN pip install -U pip wheel

WORKDIR /app

# Install app requirements
COPY --chown=lncrawl:lncrawl requirements.txt .
RUN pip install -r requirements.txt

COPY .env .env
COPY lncrawl lncrawl
COPY sources sources

ENV OUTPUT_PATH=/home/lncrawl/output
RUN mkdir -p $OUTPUT_PATH

ENTRYPOINT [ "python", "-m", "lncrawl" ]
