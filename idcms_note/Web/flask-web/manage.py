#!/usr/bin/env python
#coding=utf-8

from app import create_app, db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('default')
manager = Manager(app)

# 数据库迁移
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8001)
    manager.run()
