[program:myserver]
command=gunicorn wwebsite:app -w 2 -b 0.0.0.0:80

[supervisord]
logfile=/home/ubuntu/supervisord.log
loglevel=debug
user=root