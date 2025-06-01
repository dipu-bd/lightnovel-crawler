#!/usr/bin/env sh

VERSION=$(head -n 1 lncrawl/VERSION)

# SHLINK_API_KEY=


EXE_LINK="https://github.com/dipu-bd/lightnovel-crawler/releases/download/v$VERSION/lncrawl.exe"
EXE_TITLE="Lightnovel Crawler v$VERSION (Windows)"

LINUX_LINK="https://github.com/dipu-bd/lightnovel-crawler/releases/download/v$VERSION/lncrawl-linux"
LINUX_TITLE="Lightnovel Crawler v$VERSION (Linux)"

MAC_LINK="https://github.com/dipu-bd/lightnovel-crawler/releases/download/v$VERSION/lncrawl-mac"
MAC_TITLE="Lightnovel Crawler v$VERSION (Mac)"

set -ex

curl -X 'PATCH' \
  'https://go.bitanon.dev/rest/v3/short-urls/lncrawl-windows' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "X-Api-Key: $SHLINK_API_KEY" \
  -d '{"title": "'"$EXE_TITLE"'","longUrl": "'"$EXE_LINK"'"}'

curl -X 'PATCH' \
  'https://go.bitanon.dev/rest/v3/short-urls/lncrawl-linux' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "X-Api-Key: $SHLINK_API_KEY" \
  -d '{"title": "'"$LINUX_TITLE"'","longUrl": "'"$LINUX_LINK"'"}'
  
curl -X 'PATCH' \
  'https://go.bitanon.dev/rest/v3/short-urls/lncrawl-mac' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "X-Api-Key: $SHLINK_API_KEY" \
  -d '{"title": "'"$MAC_TITLE"'","longUrl": "'"$MAC_LINK"'"}'
  