#coding=utf-8

from flask import render_template
from . import auth
from .forms import LoginForm

@auth.route('/login')
def login():
    return render_template('loading.html')
