#####################################################
# Run this script in [SERVER] to keep alive the bot #
#####################################################

PY=python3

git checkout master
git pull origin master

$PY -m pip install --user -r requirements.txt

if [ -f "save_pid.txt" ]; then
    kill `cat save_pid.txt`
    rm -rf save_pid.txt
fi

touch bot.log
nohup $PY . > bot.log 2>&1 &
echo $! > save_pid.txt

tail -f bot.log
