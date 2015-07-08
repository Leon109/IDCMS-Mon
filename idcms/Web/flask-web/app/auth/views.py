#coding=utf-8

from flask import render_template, flash
from . import auth
from .forms import LoginForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print  form.username.data
        flash('Looks like you have changed your name!')
        return render_template('auth/loading.html', form=form)
    return render_template('auth/loading.html', form=form)
