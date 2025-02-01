from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Student, Group, Faculty, Grade, Subject

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        student_id = request.form['student_id']

        # Проверка на админа
        if first_name == "admin" and last_name == "admin" and student_id == "admin":
            session['user'] = 'admin'
            return redirect(url_for('students.students'))  # Перенаправление на страницу студентов

        # Проверка на студента
        student = Student.query.filter_by(student_id=student_id, first_name=first_name, last_name=last_name).first()
        if student:
            session['user'] = student_id  # Запоминаем ID студента в сессии
            return redirect(url_for('auth.student_dashboard', student_id=student_id))  # Перенаправление на страницу студента

        return render_template('login.html', error="Invalid credentials")  # Ошибка при неверном вводе

    return render_template('login.html')

@auth_bp.route('/student/<int:student_id>')
def student_dashboard(student_id):
    student = Student.query.get(student_id)
    if not student:
        return redirect(url_for('auth.login'))

    group = Group.query.get(student.group_id)
    faculty = Faculty.query.get(group.faculty_id) if group else None

    grades = (
        db.session.query(Subject.subject_name, Grade.grade)
        .join(Grade, Subject.subject_id == Grade.subject_id)
        .filter(Grade.student_id == student_id)
        .all()
    )

    return render_template('student_dashboard.html', student=student, faculty=faculty, group=group, grades=grades)
