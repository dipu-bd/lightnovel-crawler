#!/usr/bin/env sh

VERSION=$(head -n 1 lncrawl/VERSION)

#REBRANDLY_API_KEY=

LINUX_LINK_ID=d29bfd6a75b34993b77ac7d69869eefd
LINUX_LINK="https://github.com/dipu-bd/lightnovel-crawler/releases/download/v$VERSION/lncrawl"
LINUX_TITLE="Lightnovel Crawler v$VERSION (Linux)"

EXE_LINK_ID=8e556b9bb13e456c9bbe2c4e29aa0833
EXE_LINK="https://github.com/dipu-bd/lightnovel-crawler/releases/download/v$VERSION/lncrawl.exe"
EXE_TITLE="Lightnovel Crawler v$VERSION.exe"

set -ex
curl --request POST \
     --url "https://api.rebrandly.com/v1/links/$LINUX_LINK_ID" \
     --header 'Accept: application/json' \
     --header 'Content-Type: application/json' \
     --header "apikey: $REBRANDLY_API_KEY" \
     --data '{"destination": "'"$LINUX_LINK"'","title": "'"$LINUX_TITLE"'"}'

curl --request POST \
     --url "https://api.rebrandly.com/v1/links/$EXE_LINK_ID" \
     --header 'Accept: application/json' \
     --header 'Content-Type: application/json' \
     --header "apikey: $REBRANDLY_API_KEY" \
     --data '{"destination": "'"$EXE_LINK"'","title": "'"$EXE_TITLE"'"}'
