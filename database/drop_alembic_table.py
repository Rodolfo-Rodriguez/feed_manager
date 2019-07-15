#!/usr/bin/python

import sys
sys.path.append('/home/ubuntu/develop/feed_manager')

from sqlalchemy import inspect
from app import db

inspector = inspect(db.engine)

table_names = inspector.get_table_names()

if 'alembic_version' in table_names:
        db.engine.execute('DROP TABLE alembic_version')


print "==========================="
print "Tables"
print "==========================="

for table in table_names:
        print table
