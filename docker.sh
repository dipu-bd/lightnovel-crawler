#!/bin/sh

# Load environment variables
export $(grep -v '^#' .env | xargs -d '\n')

# Build the docker image
docker build -t lncrawl . \
  --build-arg "bot=${BOT}" \
  --build-arg "log_level=${LOG_LEVEL}" \
  --build-arg "telegram_token=${TELEGRAM_TOKEN}" \
  --build-arg "discord_token=${DISCORD_TOKEN}" \
  --build-arg "discord_signal_char=${DISCORD_SIGNAL_CHAR}"

# Run as a container
docker run --rm --name lncrawl-bot -itd lncrawl

# Unload environment variables
unset $(grep -v '^#' .env | sed -E 's/(.*)=.*/\1/' | xargs)
