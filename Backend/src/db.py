from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import os




db = SQLAlchemy()

association_table = db.Table('association',
   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
   db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    # User information
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)
    event = db.relationship('Event', secondary = association_table)
    

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password_digest = bcrypt.hashpw(kwargs.get('password').encode('utf8'),
                                            bcrypt.gensalt(rounds=13))
        self.renew_session()

    # Used to randomly generate session/update tokens
    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    # Generates new tokens, and resets expiration time
    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + \
                                datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'),
                              self.password_digest)

    # Checks if session token is valid and hasn't expired
    def verify_session_token(self, session_token):
        return session_token == self.session_token and \
            datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        return update_token == self.update_token


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, default=0)
    location = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.location = kwargs.get('location', '')
        self.time = kwargs.get('time', '')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'time': self.time
        }
