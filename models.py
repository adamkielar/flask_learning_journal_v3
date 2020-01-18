import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *


DATABASE = 'journal.db'

database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


class User(UserMixin, BaseModel):
    """Model to create user"""
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)

    @classmethod
    def create_user(cls, username, email, password):
        try:
            with database.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError("User already exists")


class Entry(BaseModel):
    """Model to create entry in journal"""
    user = ForeignKeyField(User, backref='entries')
    title = CharField()
    slug = CharField(unique=True)
    entry_date = DateField(default=datetime.date.today(), index=True)
    time_spent = IntegerField()
    what_you_learned = TextField()
    to_remember = TextField()

    @classmethod
    def create_entry(cls, user, title, slug, entry_date, time_spent, what_you_learned, to_remember):
        try:
            with database.transaction():
                cls.create(
                    user=user,
                    title=title,
                    slug=slug,
                    entry_date=entry_date,
                    time_spent=time_spent,
                    what_you_learned=what_you_learned,
                    to_remember=to_remember
                )
        except IntegrityError:
            raise ValueError("Slug already exists")


class Tag(BaseModel):
    """Model to create tag for entry"""
    entry_tag = ForeignKeyField(Entry, backref='tags')
    tag = CharField()

    @classmethod
    def create_tag(cls, entry_tag, tag):
        tag = tag['tag']
        try:
            with database.transaction():
                cls.create(
                    entry_tag=entry_tag,
                    tag=tag
                )
        except IntegrityError:
            raise ValueError("Tag already exists")


def initialize():
    """Creating tables"""
    with database:
        database.create_tables([User, Entry, Tag], safe=True)
