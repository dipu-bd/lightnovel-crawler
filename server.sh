#####################################################
# Run this script in [SERVER] to keep alive the bot #
#####################################################

git checkout master
git pull origin master

python3.6 -m pip install --user -r requirements.txt

kill -9 `cat save_pid.txt`
rm save_pid.txt

touch bot.log
nohup python3.6 . > bot.log 2>&1 &
echo $! > save_pid.txt

#tail -f bot.log
