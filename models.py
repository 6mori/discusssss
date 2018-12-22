# -*- coding: utf-8 -*-
from datetime import datetime

from setup import db

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    uname = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    register_time = db.Column(db.DateTime, default=datetime.now())
    topics = db.relationship('Topic', backref=db.backref('users'))
    comments = db.relationship('Comment', backref=db.backref('users'))

    def __str__(self):
        return '<User {} {} created at {}>'.format(self.uid, self.uname, self.register_time)

    def is_active(self):
        """
        Returns `True`.
        """
        return True

    def is_authenticated(self):
        """
        Returns `True`.
        """
        return True

    def is_anonymous(self):
        """
        Returns `False`.
        """
        return False

    def get_id(self):
        """
        Assuming that the user object has an `id` attribute, this will take
        that and convert it to `unicode`.
        """
        try:
            return str(self.uid)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override get_id")


class Topic(db.Model):
    __tablename__ = 'topics'
    pid = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    uid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete='CASCADE'))
    bid = db.Column(db.Integer, db.ForeignKey('boards.bid', ondelete='CASCADE'))
    comments = db.relationship('Comment', backref=db.backref('topics'))
    
    def __str__(self):
        return '<Topic {} created by {}>'.format(self.title[:10]+'...', \
            User.query.filter_by(uid=self.uid).first().uname)


class Comment(db.Model):
    __tablename__ = 'comments'
    cid = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    context = db.Column(db.String(512), nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete='CASCADE'))
    pid = db.Column(db.Integer, db.ForeignKey('topics.pid', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __str__(self):
        return '<Comment {} created by {} at {}>'.format(self.context[:10]+'...', \
            User.query.filter_by(uid=self.uid).first().uname, self.created_at)


class Board(db.Model):
    __tablename__ = 'boards'
    bid = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    bname = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    topics = db.relationship('Topic', backref=db.backref('boards'))
    
    def __str__(self):
        return '<Board {} created at {}>'.format(self.bname, self.created_at)


class Tag(db.Model):
    __tablename__ = 'tags'
    tid = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    tname = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __str__(self):
        return '<Tag {} created at {}>'.format(self.tname, self.created_at)


class Associated(db.Model):
    __tablename__ = 'associated'
    pid = db.Column(db.Integer, db.ForeignKey('topics.pid', ondelete='CASCADE'), primary_key=True)
    tid = db.Column(db.Integer, db.ForeignKey('tags.tid'), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __str__(self):
        return '<Topic {} associated with Tag {} by {} at {}>'.format(Topic.query.filter_by(pid=self.pid).first().title, \
            Tag.query.filter_by(tid=self.tid).first().tname, \
            User.query.filter_by(uid=self.uid).first().uname, self.created_at)



# db.drop_all()
db.create_all()

# board = Board()
# board.bname = '综合'
# db.session.add(board)
# db.session.commit()

# board = Board()
# board.bname = '游戏'
# db.session.add(board)
# db.session.commit()

# tag=Tag()
# tag.tname = '欢乐'
# db.session.add(tag)
# db.session.commit()

# tag=Tag()
# tag.tname = '引战'
# db.session.add(tag)
# db.session.commit()