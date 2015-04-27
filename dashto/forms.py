from pyramid_wtforms import SecureForm, validators
from pyramid_wtforms import PasswordField, StringField


class UserCreateForm(SecureForm):
    user_name = StringField('Username', [validators.Length(min=3, max=24)])
    user_password = PasswordField('Password', [validators.Length(min=6, max=255)])


class UserLoginForm(SecureForm):
    user_name = StringField('Username', [validators.required()])
    user_password = PasswordField('Password', [validators.required()])
