from exchangeogram import db, bcrypt, app
from flask_login import UserMixin
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList
import datetime
import json

def encoder():
    _visited = []
    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                if obj in _visited:
                    return None
                _visited.append(obj)

                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and not x.startswith('query')]:
                    val = obj.__getattribute__(field)
                    if isinstance(val, datetime.datetime):
                        fields[field] = str(val)
                    else:
                        try:
                            json.dumps(val)
                            fields[field] = val
                        except:
                            if (isinstance(val, User)):
                                fields[field] = val.displayname
                            elif isinstance(val, InstrumentedList):
                                fields[field] = []
                                for v in val:
                                    fields[field].append(v)
                            else:
                                fields[field] = None
                        
                return fields
            return json.JSONEncoder.default(self, obj)
    return Encoder

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    displayname = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    confirm_token = db.Column(db.Text)
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    notifications = db.relationship('Notification', order_by="desc(Notification.date_added)", backref='user', lazy='dynamic')

    following = db.relationship('User', lambda: folltable,
        primaryjoin=lambda: User.id == folltable.c.user_id,
        secondaryjoin=lambda: User.id == folltable.c.following_id,
        backref='followers')

    def __init__(self, username, displayname, email, cleartext_pass, confirm_token):
        self.username = username
        self.displayname = displayname
        self.email = email
        self.set_password(cleartext_pass)
        self.confirm_token = confirm_token

    # instance method
    # hashes given cleartext password and stores it
    def set_password(self, cleartext_pass):
        self.password = bcrypt.generate_password_hash(
            cleartext_pass).decode('utf-8')

    # instance method
    # checks the given cleartext password against the hash
    # returns success boolean
    def check_password(self, cleartext_pass):
        return bcrypt.check_password_hash(self.password, cleartext_pass)

folltable = db.Table(
    'folltable', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey(User.id), primary_key=True),
    db.Column('following_id', db.Integer, db.ForeignKey(User.id), primary_key=True),
)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    date_added = db.Column(db.DateTime)

    def __init__(self, user_id, message):
        if user_id == None:
            app.logger.warn("Notif created with no user ID")
        self.user_id = user_id
        self.message = message
        self.date_added = datetime.datetime.now()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    imgname = db.Column(db.Text)
    caption = db.Column(db.Text)
    date_added = db.Column(db.DateTime)
    comments = db.relationship('Comment', backref='post')
    likes = db.relationship('Like', backref='post')

    def __init__(self, user_id, imgname, caption):
        if user_id == None:
            app.logger.warn("Post created with no user ID")
        self.user_id = user_id
        self.imgname = imgname
        self.caption = caption
        self.date_added = datetime.datetime.now()


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    text = db.Column(db.Text)
    date_added = db.Column(db.DateTime)
    likes = db.relationship('Like', backref='comment')

    def __init__(self, user_id, post_id, text):
        if user_id == None or post_id == None:
            app.logger.warn("Comment created with no user ID / no post ID")
        self.user_id = user_id
        self.post_id = post_id
        self.text = text
        self.date_added = datetime.datetime.now()


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    date_added = db.Column(db.DateTime)

    def __init__(self, user_id, post_id=None, comment_id=None):
        if (post_id == None and comment_id == None) or (post_id != None and comment_id != None):
            app.logger.warn(
                "Like created with no post ID / no comment ID or both IDs specified")
        self.user_id = user_id
        self.post_id = post_id
        self.comment_id = comment_id
        self.date_added = datetime.datetime.now()
