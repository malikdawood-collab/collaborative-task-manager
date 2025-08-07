from flask_login import UserMixin
from .database import db
from datetime import datetime
import uuid

# Helper table for many-to-many relationship between User and Project
project_members = db.Table('project_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True)
)

# Helper table for many-to-many relationship between Task and Tag
task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # Relationships
    tasks_created = db.relationship('Task', foreign_keys='Task.creator_id', backref='creator', lazy=True)
    tasks_assigned = db.relationship('Task', foreign_keys='Task.assignee_id', backref='assignee', lazy=True)
    
    # Many-to-many relationship with Project
    projects = db.relationship('Project', secondary=project_members, back_populates='members', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    join_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    is_completed = db.Column(db.Boolean, nullable=False, default=False)  # ← NEW FLAG

    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    members = db.relationship('User', secondary=project_members, back_populates='projects', lazy=True)

    def __repr__(self):
        return f'<Project {self.title}, completed={self.is_completed}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    priority = db.Column(db.String(20), nullable=False, default='medium')
    
    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    # Many-to-many relationship with Tag
    tags = db.relationship('Tag', secondary=task_tags, backref='tasks', lazy=True)

    def __repr__(self):
        return f'<Task {self.title}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'
