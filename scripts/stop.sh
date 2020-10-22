#!/bin/bash

pgrep ebook-convert | xargs kill -9 >/dev/null 2>&1
pgrep python -a | grep "discord" | awk '{print $1}' | xargs kill -9 >/dev/null 2>&1
echo "Stopped all discord bots."
