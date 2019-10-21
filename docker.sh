#!/bin/sh

export BOT=console
export LOG_LEVEL=INFO

# Load environment variables
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs -d '\n')
else
  echo "No .env file found"
  exit 1
fi

# Build the docker image
docker build -t lncrawl . \
  --build-arg "bot=${BOT}" \
  --build-arg "log_level=${LOG_LEVEL}" \
  --build-arg "telegram_token=${TELEGRAM_TOKEN}" \
  --build-arg "discord_token=${DISCORD_TOKEN}" \
  --build-arg "discord_signal_char=${DISCORD_SIGNAL_CHAR}"

# Run as a container
docker stop lncrawl-${BOT}
docker run --rm \
  --name lncrawl-${BOT} \
  -itd lncrawl

# Unload environment variables
unset $(grep -v '^#' .env | sed -E 's/(.*)=.*/\1/' | xargs)
