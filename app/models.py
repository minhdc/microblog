from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),index = True,unique=True)
    email = db.Column(db.String(120),index=True,unique=True)
    pass_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen=db.Column(db.DateTime,default=datetime.utcnow)

    #followers:
    followers = db.Table('followers',
        db.Column('follower id',db.Integer,db.ForeignKey('user.id')),
        db.Column('followed id',db.Integer,db.ForeignKey('user.id'))
    )

    #followed:
    followed = db.relationship(
        'User',secondary=followers,
        primaryjoin=(followers.c.follower_id==id),
        secondaryjoin=(followers.c.followed_id==id),
        backref=db.backref('followers',lazy='dynamic'),
        lazy='dynamic'    
    )


    #tell Python how to print objects of this class
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_pass(self,password):
        self.pass_hash = generate_password_hash(password)

    def check_pass(self,password):
        return check_password_hash(self.pass_hash,password)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)


class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
