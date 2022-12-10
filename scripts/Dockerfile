FROM selenium/standalone-chrome:latest

USER root
# Install general dependencies
RUN apt-get update -yq \
    && apt-get install -yq \
    wget tar xz-utils make cmake g++ \
    python3-dev python3-pip python3-tk \
    && apt-get clean autoclean \
    && apt-get autoremove -yq

# Install calibre dependencies
RUN apt-get install -yq libffi-dev libegl1 libopengl0 \
    libnss3 libgl1-mesa-glx libxcomposite1 libxrandr2 \
    libxi6 fontconfig libxkbcommon-x11-0 libxtst6 libxkbfile1 \
    && apt-get clean autoclean \
    && apt-get autoremove -yq

# Install calibre
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin \
    && ln -s /opt/calibre/ebook-convert /usr/local/bin/ebook-convert

# Setup the app environment
WORKDIR /home/seluser/app
USER seluser

# Install global requirements
RUN alias python=python3
RUN alias pip=pip3
RUN export PATH="/home/seluser/.local/bin:$PATH"
RUN pip install -U pip wheel setuptools

# Install app requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source files
COPY sources sources
COPY lncrawl lncrawl

# Grant access to source files
USER root
RUN chown -R seluser:seluser /home/seluser/app
ARG VNC_PASSWORD
RUN x11vnc -storepasswd "$VNC_PASSWORD" /home/seluser/.vnc/passwd

# Switch to seluser
USER seluser
COPY scripts/entry_point.sh entry_point.sh

ENTRYPOINT [ "bash", "entry_point.sh" ]
