import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "notethat_secret"

# Configure the database URI using environment variable or default to SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///notethat.db")
# Ensure compatibility: if using Railway’s postgres URL, replace prefix.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Association table for many-to-many relationship between Groups and Users
group_members = db.Table('group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'  # Renamed to avoid conflict with reserved word "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(200), default="default.png")
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    notes = db.relationship("Note", backref="user", lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    members = db.relationship('User', secondary=group_members, backref=db.backref('groups', lazy='dynamic'))

class GroupNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    note_title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.String(100))

class TimeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    group_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50))
    timestamp = db.Column(db.String(100))
