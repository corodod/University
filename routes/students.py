from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Faculty, Group, Student, StudentIDCard, Grade, Subject
from datetime import date

students_bp = Blueprint('students', __name__)


@students_bp.route('/students', methods=['GET', 'POST'])
def students():
    faculties = Faculty.query.all()
    groups = Group.query.all()

    filters = {
        'faculty_id': request.args.get('faculty'),
        'group_id': request.args.get('group'),
        'gender': request.args.get('gender')
    }

    page = request.args.get('page', 1, type=int)
    per_page = 10

    if request.method == 'POST':
        new_student = Student(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            birth_date=request.form['birth_date'],
            gender=request.form['gender'],
            group_id=request.form['group_id']
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

        faculty_id = Group.query.filter_by(group_id=new_student.group_id).first().faculty_id
        subjects = Subject.query.filter_by(faculty_id=faculty_id).limit(4).all()

        for subject in subjects:
            new_grade = Grade(student_id=student_id, subject_id=subject.subject_id, grade=0, exam_date=date.today())
            db.session.add(new_grade)
        db.session.commit()

        return redirect(url_for('students.students'))

    students_query = Student.query
    if filters['faculty_id']:
        students_query = students_query.join(Group).filter(Group.faculty_id == filters['faculty_id'])
    if filters['group_id']:
        students_query = students_query.filter(Student.group_id == filters['group_id'])
    if filters['gender']:
        students_query = students_query.filter(Student.gender == filters['gender'])

    students = students_query.paginate(page=page, per_page=per_page)

    return render_template(
        'students.html',
        students=students.items,
        faculties=faculties,
        groups=groups,
        filters=filters,
        page=page,
        total_pages=students.pages,
        total_students=students.total  # Добавляем total_students
    )


# @students_bp.route('/students', methods=['GET', 'POST'])
# def students():
#     faculties = Faculty.query.all()
#     groups = Group.query.all()

#     filters = {
#         'faculty_id': request.args.get('faculty'),
#         'group_id': request.args.get('group'),
#         'gender': request.args.get('gender')
#     }

#     page = request.args.get('page', 1, type=int)
#     per_page = 10

#     if request.method == 'POST':
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

#         new_card = StudentIDCard(
#             student_id=student_id,
#             registration_date=date.today(),
#             expiration_date=date.today().replace(year=date.today().year + 4),
#             type="electronic"
#         )
#         db.session.add(new_card)

#         faculty_id = Group.query.filter_by(group_id=new_student.group_id).first().faculty_id
#         subjects = Subject.query.filter_by(faculty_id=faculty_id).limit(4).all()

#         for subject in subjects:
#             new_grade = Grade(student_id=student_id, subject_id=subject.subject_id, grade=0, exam_date=date.today())
#             db.session.add(new_grade)
#         db.session.commit()

#         return redirect(url_for('students.students'))

#     students_query = Student.query
#     if filters['faculty_id']:
#         students_query = students_query.join(Group).filter(Group.faculty_id == filters['faculty_id'])
#     if filters['group_id']:
#         students_query = students_query.filter(Student.group_id == filters['group_id'])
#     if filters['gender']:
#         students_query = students_query.filter(Student.gender == filters['gender'])

#     students = students_query.paginate(page=page, per_page=per_page)

#     # return render_template('students.html', students=students.items, faculties=faculties, groups=groups, filters=filters)
#     return render_template(
#     'students.html',
#     students=students.items,
#     faculties=faculties,
#     groups=groups,
#     filters=filters,
#     page=page,
#     total_pages=students.pages  # Добавляем total_pages
#     )


