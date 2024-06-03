from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired, Length, ValidationError, StopValidation, Email, Regexp
from sqlalchemy import or_

from exchangeogram.models import User


def check_duplicate(keyname):
    def _check_duplicate(form, field):
        if User.query.filter(getattr(User, keyname).like(field.data)).first() is not None:
            raise ValidationError("Registration form dupliate unique field!")
    return _check_duplicate


class SignupForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(
        message="Invalid Email!"), check_duplicate('email')])
    username = StringField(
        validators=[InputRequired(), Regexp('^\w+$', message='Username must be alphanumeric'), check_duplicate('username')])
    displayname = StringField(validators=[InputRequired()])
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, message="Password too short!")])


class LoginForm(FlaskForm):
    user_identifier = StringField(validators=[InputRequired()])

    def validate_user_identifier(form, field):
        user = User.query.filter(or_(User.username == field.data, User.email == field.data)).first()
        if user is None:
            raise StopValidation(message="Invalid Credentials!")
        if user.confirm_token:
            raise StopValidation(message="Account is not yet confirmed")
    
    password = PasswordField(validators=[InputRequired()])

    def validate_password(form, field):
        user = User.query.filter(or_(User.username == form.user_identifier.data, User.email == form.user_identifier.data)).first()
        if user is not None and not user.check_password(field.data):
            raise StopValidation(message="Invalid Credentials!")
        form.user = user



class PostForm(FlaskForm):
    image = FileField(validators=[FileRequired(),FileAllowed(['jpg','png','gif','jpeg'])])
    caption = StringField(validators=[InputRequired()])


class CommentForm(FlaskForm):
    pass
