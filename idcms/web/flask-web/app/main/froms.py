from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField(validators=[Required()])
    passwd = PasswordField(validators=[Required()])
    submit = SubmitField('Read me')
