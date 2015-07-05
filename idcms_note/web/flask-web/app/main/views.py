from flask import render_template, flash
from . import main
from .froms import NameForm

@main.route('/',  methods=['GET', 'POST'])
def hello_world():
    form = NameForm()
    if form.validate_on_submit():
        flash('Looks like you have changed your name!')
        return render_template('loading.html', form=form)
    return render_template('loading.html', form=form)
