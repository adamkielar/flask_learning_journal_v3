from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, FormField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User, Tag


def name_exists(form, field):
    """Checks if name is in database"""
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    """Checks if email is in database"""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('Email already exists.')


class RegisterForm(FlaskForm):
    """Form for user to register"""
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), email_exists]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=4),
            EqualTo('password2', message='Password must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )


class LoginForm(FlaskForm):
    """Form for user to log in"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(FlaskForm):
    """Form for user to add entry"""
    title = StringField('Title', validators=[DataRequired(message='You must add title')])
    entry_date = DateField('Entry Date (2020-01-16)', format='%Y-%m-%d',
                           validators=[DataRequired(message='You must enter date in format (2020-01-16)')])
    time_spent = StringField('Time Spent (hours)')
    what_you_learned = TextAreaField('What You Learned ?')
    to_remember = TextAreaField('Resources to Remember')


class TagForm(FlaskForm):
    """For for user to add tag"""
    tag = StringField('Tags')


class TagEntryForm(FlaskForm):
    """Form with FormField to submit forms separately """
    entry_form = FormField(EntryForm)
    tag_form = FormField(TagForm)

    

