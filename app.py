from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модели
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

# Маршруты
@app.route('/')
def index():
    return redirect(url_for('students'))

@app.route('/students', methods=['GET', 'POST'])
def students():
    faculties = Faculty.query.all()
    groups = Group.query.all()

    filters = {
        'faculty_id': request.args.get('faculty'),
        'group_id': request.args.get('group'),
        'gender': request.args.get('gender')
    }

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birth_date = request.form['birth_date']
        gender = request.form['gender']
        group_id = request.form['group_id']

        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            group_id=group_id
        )
        db.session.add(new_student)
        db.session.commit()

        student_id = new_student.student_id

        new_card = StudentIDCard(
            student_id=student_id,
            registration_date=date.today(),
            expiration_date=date.today().replace(year=date.today().year + 4),
            type="electronic"
        )
        db.session.add(new_card)

        faculty_id = Group.query.filter_by(group_id=group_id).first().faculty_id
        subjects = Subject.query.filter_by(faculty_id=faculty_id).limit(4).all()

        for subject in subjects:
            new_grade = Grade(student_id=student_id, subject_id=subject.subject_id, grade=0, exam_date=date.today())
            db.session.add(new_grade)
        db.session.commit()

        return redirect(url_for('students', faculty=filters['faculty_id'], group=filters['group_id'], gender=filters['gender']))

    students_query = Student.query

    if filters['faculty_id']:
        students_query = students_query.join(Group).filter(Group.faculty_id == filters['faculty_id'])
    if filters['group_id']:
        students_query = students_query.filter(Student.group_id == filters['group_id'])
    if filters['gender']:
        students_query = students_query.filter(Student.gender == filters['gender'])

    students = students_query.all()

    return render_template('students.html', students=students, faculties=faculties, groups=groups, filters=filters)

@app.route('/grades', methods=['GET', 'POST'])
def grades():
    faculties = Faculty.query.all()
    groups = Group.query.all()

    filters = {
        'faculty_id': request.args.get('faculty'),
        'group_id': request.args.get('group'),
        'min_grade': request.args.get('min_grade'),
        'max_grade': request.args.get('max_grade'),
        'subject_name': request.args.get('subject_name')  # Добавляем новый фильтр
    }

    grades_query = (
        db.session.query(
            Grade,
            Student.first_name,
            Student.last_name,
            Subject.subject_name
        )
        .join(Student)
        .join(Subject)
        .join(Group)
    )

    if filters['faculty_id']:
        grades_query = grades_query.filter(Group.faculty_id == filters['faculty_id'])
    if filters['group_id']:
        grades_query = grades_query.filter(Student.group_id == filters['group_id'])
    if filters['min_grade']:
        grades_query = grades_query.filter(Grade.grade >= filters['min_grade'])
    if filters['max_grade']:
        grades_query = grades_query.filter(Grade.grade <= filters['max_grade'])
    if filters['subject_name']:
        grades_query = grades_query.filter(Subject.subject_name.ilike(f"%{filters['subject_name']}%"))  # Фильтрация по названию предмета

    grades = grades_query.all()

    return render_template('grades.html', grades=grades, faculties=faculties, groups=groups, filters=filters)

@app.route('/edit_grade/<int:student_id>/<int:subject_id>', methods=['GET', 'POST'])
def edit_grade(student_id, subject_id):
    grade = Grade.query.filter_by(student_id=student_id, subject_id=subject_id).first()

    if request.method == 'POST':
        new_grade_value = request.form['grade']
        grade.grade = new_grade_value
        db.session.commit()
        return redirect(url_for('grades', faculty=request.args.get('faculty'), group=request.args.get('group'), min_grade=request.args.get('min_grade'), max_grade=request.args.get('max_grade')))

    return render_template('edit_grade.html', grade=grade)
@app.route('/subjects', methods=['GET'])
def subjects():
    faculties = Faculty.query.all()

    # Фильтр по факультету
    faculty_id = request.args.get('faculty')

    if faculty_id:
        subjects = Subject.query.filter_by(faculty_id=faculty_id).all()
    else:
        subjects = Subject.query.all()

    return render_template('subjects.html', subjects=subjects, faculties=faculties, selected_faculty=faculty_id)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    Grade.query.filter_by(student_id=student_id).delete()# Удаление оценок студента
    StudentIDCard.query.filter_by(student_id=student_id).delete()# Удаление зачетной книжки студента
    student = Student.query.get(student_id)# Удаление самого студента
    db.session.delete(student)

    db.session.commit()# Применение изменений
    return redirect(url_for('students'))


if __name__ == '__main__':
    app.run(debug=True)
