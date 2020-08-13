export LC_ALL="en_US.UTF-8"

git stash save -u
git fetch origin master
git rebase
git stash pop

if [ ! -d venv ]; then
    python -m venv venv
fi

. venv/bin/activate
pip install -U -r requirements.txt
pip install -U -r dev-requirements.txt

echo "Stopping previous instances..."
pgrep python -a | grep "discord" | awk '{print $1}' | xargs kill -9 || true

if [ "$1" = "stop" ]; then
    exit 0
fi

echo "Starting new instances..."
nohup python3 . --bot discord --shard-id 0 --shard-count 2 >/dev/null 2>&1 &
nohup python3 . --bot discord --shard-id 1 --shard-count 2 >/dev/null 2>&1 &

echo "Done."
