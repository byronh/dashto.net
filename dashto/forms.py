from pyramid_wtforms import SecureForm, validators
from pyramid_wtforms import FileField, IntegerField, PasswordField, StringField, TextAreaField


class CampaignCreateForm(SecureForm):
    campaign_name = StringField('Name', [validators.Length(min=3, max=64)])
    campaign_description = TextAreaField('Description')


class CampaignRequestJoinForm(SecureForm):
    campaign_id = IntegerField([validators.required()])


class CharacterCreateForm(SecureForm):
    character_name = StringField('Name', [validators.Length(min=2, max=64)])


class CharacterEditForm(SecureForm):
    character_name = StringField('Name', [validators.Length(min=2, max=64)])
    character_full_name = StringField('Full Name')
    character_biography = TextAreaField('Biography')
    character_portrait = FileField('Portrait')


class ChatForm(SecureForm):
    pass


class UserCreateForm(SecureForm):
    user_name = StringField('Username', [validators.Length(min=3, max=24)])
    user_password = PasswordField('Password', [validators.Length(min=6, max=255)])


class UserLoginForm(SecureForm):
    user_name = StringField('Username', [validators.required()])
    user_password = PasswordField('Password', [validators.required()])
