from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length


class LoginForm(Form):
    username = StringField('Username', validators=[Required(), Length(1, 12)])
    password = PasswordField('Password',  validators=[Required()])
    rememberme = BooleanField("test")
    submit = SubmitField('Log In')
