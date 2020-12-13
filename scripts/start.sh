#!/bin/bash
export LC_ALL="en_US.UTF-8"

shards=4
curdir="$(dirname "$(readlink -f "$0")")"
cd "$(dirname "$curdir")"
echo "Workdir: $(pwd)"

echo "Fetch updates..."
git stash save -u
git fetch origin master
git rebase FETCH_HEAD
git stash pop

echo "Setup virtual environment..."
if [ ! -d venv ]; then
    python -m venv venv
fi
. venv/bin/activate
pip install -U -r requirements.txt
pip install -U -r dev-requirements.txt

echo "Stopping previous instances..."
/bin/bash scripts/stop.sh

echo "Starting $shards shards..."
for i in $(seq $shards)
do
    echo "Starting shard $((i-1)) of $shards shards..." &&
    python . --bot discord --shard-id $((i-1)) --shard-count $shards &&
    echo "Stopped shard $((i-1)) of $shards shards." &
done
wait

echo "Force stop remaining instances..."
/bin/bash scripts/stop.sh
