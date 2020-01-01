#####################################################
# Run this script in [SERVER] to keep alive the bot #
#####################################################

git checkout master
git pull origin master

python3 -m pip install --user -r requirements.txt

if [ -f "save_pid.txt" ]; then
    kill -9 `cat save_pid.txt`
    rm -rf save_pid.txt
fi

touch bot.log
nohup python3 . > bot.log 2>&1 &
echo $! > save_pid.txt

tail -f bot.log
