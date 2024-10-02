from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
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
    gender = db.Column(db.String(1), nullable=False)  # Измените тип на character(1)
    group_id = db.Column(db.Integer, db.ForeignKey('schema.groups.group_id'))

    group = db.relationship('Group', backref='students')

class StudentIDCard(db.Model):
    __tablename__ = 'student_id_card'
    __table_args__ = {'schema': 'schema'}
    card_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('schema.students.student_id'))
    registration_date = db.Column(db.Date, nullable=False, default=date.today)
    expiration_date = db.Column(db.Date, nullable=False)
    card_type = db.Column(db.String(20), nullable=False, default="electronic")

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

# Routes
@app.route('/')
def index():
    return redirect(url_for('students'))

@app.route('/students', methods=['GET', 'POST'])
def students():
    faculties = Faculty.query.all()
    groups = Group.query.all()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birth_date = request.form['birth_date']
        gender = request.form['gender']  # Получаем значение 'M' или 'F'
        group_id = request.form['group_id']

        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            group_id=group_id
        )
        db.session.add(new_student)
        db.session.commit()  # Коммитим изменения после добавления студента

        # Получаем student_id только после того, как объект был добавлен и коммит
        student_id = new_student.student_id

        new_card = StudentIDCard(
            student_id=student_id,
            registration_date=date.today(),
            expiration_date=date.today().replace(year=date.today().year + 4),
            card_type="electronic"
        )
        db.session.add(new_card)  # Добавляем карточку студента

        # Добавляем новые оценки
        faculty_id = Group.query.filter_by(group_id=group_id).first().faculty_id
        subjects = Subject.query.filter_by(faculty_id=faculty_id).limit(4).all()

        for subject in subjects:
            new_grade = Grade(student_id=student_id, subject_id=subject.subject_id, grade=None)
            db.session.add(new_grade)
        db.session.commit()  # Коммитим изменения после добавления карточки и оценок

        return redirect(url_for('students'))

    filters = {
        'faculty_id': request.args.get('faculty'),
        'group_id': request.args.get('group'),
        'gender': request.args.get('gender')
    }
    students_query = Student.query

    if filters['faculty_id']:
        students_query = students_query.join(Group).filter(Group.faculty_id == filters['faculty_id'])
    if filters['group_id']:
        students_query = students_query.filter(Student.group_id == filters['group_id'])
    if filters['gender']:
        students_query = students_query.filter(Student.gender == filters['gender'])

    students = students_query.all()

    return render_template('students.html', students=students, faculties=faculties, groups=groups)


@app.route('/grades', methods=['GET', 'POST'])
def grades():
    faculties = Faculty.query.all()
    groups = Group.query.all()

    filters = {
        'faculty_id': request.args.get('faculty'),
        'group_id': request.args.get('group'),
        'min_grade': request.args.get('min_grade'),
        'max_grade': request.args.get('max_grade')
    }
    grades_query = Grade.query.join(Student).join(Group)

    if filters['faculty_id']:
        grades_query = grades_query.filter(Group.faculty_id == filters['faculty_id'])
    if filters['group_id']:
        grades_query = grades_query.filter(Student.group_id == filters['group_id'])
    if filters['min_grade']:
        grades_query = grades_query.filter(Grade.grade >= filters['min_grade'])
    if filters['max_grade']:
        grades_query = grades_query.filter(Grade.grade <= filters['max_grade'])

    grades = grades_query.all()

    return render_template('grades.html', grades=grades, faculties=faculties, groups=groups)

if __name__ == '__main__':
    app.run(debug=True)
