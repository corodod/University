from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Faculty(db.Model):
    __tablename__ = 'faculties'
    __table_args__ = {'schema': 'schema'}
    faculty_id = db.Column(db.Integer, primary_key=True)
    faculty_name = db.Column(db.String(255), nullable=False)
    dean = db.Column(db.String(255), nullable=False)

class Group(db.Model):
    __tablename__ = 'groups'
    __table_args__ = {'schema': 'schema'}
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(255))
    faculty_id = db.Column(db.Integer, db.ForeignKey('schema.faculties.faculty_id'))

class Student(db.Model):
    __tablename__ = 'students'
    __table_args__ = {'schema': 'schema'}
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('schema.groups.group_id'))

    group = db.relationship('Group', backref='students')

class StudentIDCard(db.Model):
    __tablename__ = 'student_id_card'
    __table_args__ = {'schema': 'schema'}
    card_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('schema.students.student_id'))
    registration_date = db.Column(db.Date, nullable=False, default=date.today)
    expiration_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False, default="electronic")

class Grade(db.Model):
    __tablename__ = 'grades'
    __table_args__ = {'schema': 'schema'}
    student_id = db.Column(db.Integer, db.ForeignKey('schema.students.student_id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('schema.subjects.subject_id'), primary_key=True)
    grade = db.Column(db.Numeric(3, 2), nullable=True)
    exam_date = db.Column(db.Date, nullable=False)

class Subject(db.Model):
    __tablename__ = 'subjects'
    __table_args__ = {'schema': 'schema'}
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(255), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('schema.faculties.faculty_id'))
