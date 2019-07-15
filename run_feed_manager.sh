gunicorn --threads 5 --bind 0.0.0.0:8000 --chdir /home/ubuntu/develop/feed_manager feed_manager:app 
