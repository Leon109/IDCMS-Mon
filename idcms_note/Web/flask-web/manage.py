#!/usr/bin/env python

from app import create_app

app = create_app('default')
app.run(host='0.0.0.0', port=8001)
