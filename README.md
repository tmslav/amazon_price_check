# amazon_price_check
##INSTALATION
```
sudo apt-get install libxml2-dev libxslt-dev python-dev zlib1g-dev tmux
sudo apt-get install python-virutalenv
virtualenv --no-site-packages env
git clone https://github.com/tmslav/amazon_price_check.git
cd amazon_price_check
pip install -r req.txt

```

##STARTING
```
tmux new session
```
Navigate to directory where script is located and check if redis server is installed.

```
python run.py

Press <Ctrl -B>C

celery -A app.celery_app beat

Press <Ctrl -B>C

celery -A app.celery_app worker

```
