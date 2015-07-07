#!/usr/bin/env python

from app import create_app

app = create_app('default')

print app.url_map
app.run(host='0.0.0.0', port=8000)
