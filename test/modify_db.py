#!/usr/bin/python2

import sys

sys.path.append('/home/ubuntu/develop/radio-v3')

from app import db
from app.models import Episode

episode_list = Episode.query.all()

for episode in episode_list:
    episode.downloaded = False 
    db.session.commit()
