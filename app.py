from flask import Flask, redirect, url_for
from models import db
from routes.students import students_bp
from routes.grades import grades_bp
from routes.subjects import subjects_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(students_bp)
app.register_blueprint(grades_bp)
app.register_blueprint(subjects_bp)

@app.route('/')
def index():
    return redirect(url_for('students.students'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

















# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from datetime import date

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # Модели
# class Faculty(db.Model):
#     __tablename__ = 'faculties'
#     __table_args__ = {'schema': 'schema'}
#     faculty_id = db.Column(db.Integer, primary_key=True)
#     faculty_name = db.Column(db.String(255), nullable=False)
#     dean = db.Column(db.String(255), nullable=False)

# class Group(db.Model):
#     __tablename__ = 'groups'
#     __table_args__ = {'schema': 'schema'}
#     group_id = db.Column(db.Integer, primary_key=True)
#     group_name = db.Column(db.String(100), nullable=False)
#     course = db.Column(db.Integer, nullable=False)
#     specialization = db.Column(db.String(255))
#     faculty_id = db.Column(db.Integer, db.ForeignKey('schema.faculties.faculty_id'))

# class Student(db.Model):
#     __tablename__ = 'students'
#     __table_args__ = {'schema': 'schema'}
#     student_id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(100), nullable=False)
#     last_name = db.Column(db.String(100), nullable=False)
#     birth_date = db.Column(db.Date, nullable=False)
#     gender = db.Column(db.String(1), nullable=False)
#     group_id = db.Column(db.Integer, db.ForeignKey('schema.groups.group_id'))

#     group = db.relationship('Group', backref='students')

# class StudentIDCard(db.Model):
#     __tablename__ = 'student_id_card'
#     __table_args__ = {'schema': 'schema'}
#     card_id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('schema.students.student_id'))
#     registration_date = db.Column(db.Date, nullable=False, default=date.today)
#     expiration_date = db.Column(db.Date, nullable=False)
#     type = db.Column(db.String(20), nullable=False, default="electronic")

# class Grade(db.Model):
#     __tablename__ = 'grades'
#     __table_args__ = {'schema': 'schema'}
#     student_id = db.Column(db.Integer, db.ForeignKey('schema.students.student_id'), primary_key=True)
#     subject_id = db.Column(db.Integer, db.ForeignKey('schema.subjects.subject_id'), primary_key=True)
#     grade = db.Column(db.Numeric(3, 2), nullable=True)
#     exam_date = db.Column(db.Date, nullable=False)

# class Subject(db.Model):
#     __tablename__ = 'subjects'
#     __table_args__ = {'schema': 'schema'}
#     subject_id = db.Column(db.Integer, primary_key=True)
#     subject_name = db.Column(db.String(255), nullable=False)
#     hours = db.Column(db.Integer, nullable=False)
#     faculty_id = db.Column(db.Integer, db.ForeignKey('schema.faculties.faculty_id'))

# # Маршруты
# @app.route('/')
# def index():
#     return redirect(url_for('students'))

# @app.route('/students', methods=['GET', 'POST'])
# def students():
#     faculties = Faculty.query.all()
#     groups = Group.query.all()

#     filters = {
#         'faculty_id': request.args.get('faculty'),
#         'group_id': request.args.get('group'),
#         'gender': request.args.get('gender')
#     }

#     page = request.args.get('page', 1, type=int)  # Текущая страница
#     per_page = 10  # Количество студентов на странице

#     if request.method == 'POST':
#         # Добавляем нового студента
#         new_student = Student(
#             first_name=request.form['first_name'],
#             last_name=request.form['last_name'],
#             birth_date=request.form['birth_date'],
#             gender=request.form['gender'],
#             group_id=request.form['group_id']
#         )
#         db.session.add(new_student)
#         db.session.commit()

#         student_id = new_student.student_id

#         # Добавляем студенческий билет
#         new_card = StudentIDCard(
#             student_id=student_id,
#             registration_date=date.today(),
#             expiration_date=date.today().replace(year=date.today().year + 4),
#             type="electronic"
#         )
#         db.session.add(new_card)

#         # Автоматически добавляем оценки по предметам факультета
#         faculty_id = Group.query.filter_by(group_id=new_student.group_id).first().faculty_id
#         subjects = Subject.query.filter_by(faculty_id=faculty_id).limit(4).all()

#         for subject in subjects:
#             new_grade = Grade(student_id=student_id, subject_id=subject.subject_id, grade=0, exam_date=date.today())
#             db.session.add(new_grade)
#         db.session.commit()

#         return redirect(url_for('students', faculty=filters['faculty_id'], group=filters['group_id'], gender=filters['gender']))

#     # Фильтрация студентов
#     students_query = Student.query

#     if filters['faculty_id']:
#         students_query = students_query.join(Group).filter(Group.faculty_id == filters['faculty_id'])
#     if filters['group_id']:
#         students_query = students_query.filter(Student.group_id == filters['group_id'])
#     if filters['gender']:
#         students_query = students_query.filter(Student.gender == filters['gender'])

#     # Пагинация
#     students = students_query.paginate(page=page, per_page=per_page)
#     total_students = students_query.count()

#     return render_template(
#         'students.html',
#         students=students.items,
#         faculties=faculties,
#         groups=groups,
#         filters=filters,
#         total_students=total_students,
#         page=page,
#         total_pages=students.pages  # Общее количество страниц
#     )

# @app.route('/grades', methods=['GET', 'POST'])
# def grades():
#     faculties = Faculty.query.all()
#     groups = Group.query.all()

#     # Фильтры для оценок
#     filters = {
#         'faculty_id': request.args.get('faculty'),
#         'group_id': request.args.get('group'),
#         'min_grade': request.args.get('min_grade'),
#         'max_grade': request.args.get('max_grade'),
#         'subject_name': request.args.get('subject_name'),
#         'sort_order': request.args.get('sort_order', 'asc')  # Сортировка
#     }

#     # Параметры пагинации
#     page = int(request.args.get('page', 1))  # Номер текущей страницы
#     per_page = 10                           # Количество записей на странице

#     # Базовый запрос
#     grades_query = (
#         db.session.query(
#             Grade,
#             Student.first_name,
#             Student.last_name,
#             Subject.subject_name
#         )
#         .join(Student)
#         .join(Subject)
#         .join(Group)
#     )

#     # Применяем фильтры
#     if filters['faculty_id']:
#         grades_query = grades_query.filter(Group.faculty_id == filters['faculty_id'])
#     if filters['group_id']:
#         grades_query = grades_query.filter(Student.group_id == filters['group_id'])
#     if filters['min_grade']:
#         grades_query = grades_query.filter(Grade.grade >= filters['min_grade'])
#     if filters['max_grade']:
#         grades_query = grades_query.filter(Grade.grade <= filters['max_grade'])
#     if filters['subject_name']:
#         grades_query = grades_query.filter(Subject.subject_name.ilike(f"%{filters['subject_name']}%"))

#     # Применяем сортировку
#     if filters['sort_order'] == 'asc':
#         grades_query = grades_query.order_by(Grade.grade.asc())
#     else:
#         grades_query = grades_query.order_by(Grade.grade.desc())

#     # Общее количество записей (для подсчета страниц)
#     total_grades = grades_query.count()

#     # Пагинация (LIMIT и OFFSET)
#     grades_query = grades_query.limit(per_page).offset((page - 1) * per_page)
#     grades = grades_query.all()

#     # Вычисляем общее количество страниц
#     total_pages = (total_grades + per_page - 1) // per_page

#     return render_template(
#         'grades.html',
#         grades=grades,
#         faculties=faculties,
#         groups=groups,
#         filters=filters,
#         page=page,
#         total_pages=total_pages,
#         total_grades=total_grades
#     )

# @app.route('/edit_grade/<int:student_id>/<int:subject_id>', methods=['GET', 'POST'])
# def edit_grade(student_id, subject_id):
#     grade = Grade.query.filter_by(student_id=student_id, subject_id=subject_id).first()

#     if request.method == 'POST':
#         grade.grade = request.form['grade']
#         db.session.commit()
#         return redirect(url_for('grades', faculty=request.args.get('faculty'), group=request.args.get('group'), min_grade=request.args.get('min_grade'), max_grade=request.args.get('max_grade')))

#     return render_template('edit_grade.html', grade=grade)
# @app.route('/subjects', methods=['GET', 'POST'])
# def subjects():
#     faculties = Faculty.query.all()
#     faculty_id = request.args.get('faculty')
#     page = request.args.get('page', 1, type=int)  # Текущая страница
#     per_page = 10  # Количество предметов на странице

#     if request.method == 'POST':
#         # Добавляем новый предмет
#         subject_name = request.form['subject_name']
#         hours = request.form['hours']
#         faculty_id = request.form['faculty_id']

#         new_subject = Subject(subject_name=subject_name, hours=hours, faculty_id=faculty_id)
#         db.session.add(new_subject)
#         db.session.commit()

#         # Добавляем оценки по новому предмету для всех студентов данного факультета
#         students = Student.query.join(Group).filter(Group.faculty_id == faculty_id).all()
#         for student in students:
#             new_grade = Grade(student_id=student.student_id, subject_id=new_subject.subject_id, grade=0,
#                               exam_date=date.today())
#             db.session.add(new_grade)
#         db.session.commit()

#         return redirect(url_for('subjects', faculty=faculty_id))

#     # Фильтрация
#     subjects_query = Subject.query
#     if faculty_id:
#         subjects_query = subjects_query.filter_by(faculty_id=faculty_id)

#     # Пагинация
#     subjects = subjects_query.paginate(page=page, per_page=per_page)
#     total_subjects = subjects_query.count()  # Общее количество предметов

#     return render_template(
#         'subjects.html',
#         subjects=subjects.items,
#         faculties=faculties,
#         selected_faculty=faculty_id,
#         total_subjects=total_subjects,
#         page=page,
#         total_pages=subjects.pages  # Общее количество страниц
#     )


# @app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
# def edit_subject(subject_id):
#     subject = Subject.query.get(subject_id)

#     if request.method == 'POST':
#         # Обновляем название предмета и количество часов
#         subject.subject_name = request.form['subject_name']
#         subject.hours = request.form['hours']
#         db.session.commit()
#         return redirect(url_for('subjects', faculty=subject.faculty_id))

#     return render_template('edit_subject.html', subject=subject)


# @app.route('/delete_subject/<int:subject_id>', methods=['POST'])
# def delete_subject(subject_id):
#     # Удаляем оценки по этому предмету у всех студентов
#     Grade.query.filter_by(subject_id=subject_id).delete()

#     # Удаляем предмет из базы данных
#     subject = Subject.query.get(subject_id)
#     db.session.delete(subject)
#     db.session.commit()

#     return redirect(url_for('subjects', faculty=subject.faculty_id))


# @app.route('/delete_student/<int:student_id>', methods=['POST'])
# def delete_student(student_id):
#     Grade.query.filter_by(student_id=student_id).delete()
#     StudentIDCard.query.filter_by(student_id=student_id).delete()
#     student = Student.query.get(student_id)
#     db.session.delete(student)
#     db.session.commit()
#     return redirect(url_for('students'))

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)
