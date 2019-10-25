#####################################################
# Run this script in [SERVER] to keep alive the bot #
#####################################################

PY=python3

git checkout master
git pull origin master

$PY -m pip install --user -r requirements.txt

kill -9 `cat save_pid.txt`
rm save_pid.txt

touch bot.log
nohup $PY . > bot.log 2>&1 &
echo $! > save_pid.txt

#tail -f bot.log
