from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Grade, Student, Subject, Group

grades_bp = Blueprint('grades', __name__)

@grades_bp.route('/grades', methods=['GET', 'POST'])
def grades():
    faculties = Group.query.with_entities(Group.faculty_id).distinct()
    groups = Group.query.all()

    filters = {
        'faculty_id': request.args.get('faculty'),
        'group_id': request.args.get('group'),
        'subject_name': request.args.get('subject_name'),
        'min_grade': request.args.get('min_grade'),
        'max_grade': request.args.get('max_grade'),
        'sort_order': request.args.get('sort_order', 'asc')
    }

    page = request.args.get('page', 1, type=int)
    per_page = 10

    grades_query = db.session.query(Grade, Student.first_name, Student.last_name, Subject.subject_name) \
        .join(Student) \
        .join(Subject) \
        .join(Group)

    # Применяем фильтры
    if filters['faculty_id']:
        grades_query = grades_query.filter(Group.faculty_id == filters['faculty_id'])
    if filters['group_id']:
        grades_query = grades_query.filter(Student.group_id == filters['group_id'])
    if filters['subject_name']:
        grades_query = grades_query.filter(Subject.subject_name.ilike(f"%{filters['subject_name']}%"))
    if filters['min_grade']:
        grades_query = grades_query.filter(Grade.grade >= filters['min_grade'])
    if filters['max_grade']:
        grades_query = grades_query.filter(Grade.grade <= filters['max_grade'])

    # Применяем сортировку
    if filters['sort_order'] == 'asc':
        grades_query = grades_query.order_by(Grade.grade.asc())
    else:
        grades_query = grades_query.order_by(Grade.grade.desc())

    # Подсчет общего количества оценок (учитывая фильтрацию)
    total_grades = grades_query.count()

    grades = grades_query.paginate(page=page, per_page=per_page)

    return render_template(
        'grades.html',
        grades=grades.items,
        faculties=faculties,
        groups=groups,
        filters=filters,
        page=page,
        total_pages=grades.pages,
        total_grades=total_grades  # Передаем total_grades в шаблон
    )


@grades_bp.route('/edit_grade/<int:student_id>/<int:subject_id>', methods=['GET', 'POST'])
def edit_grade(student_id, subject_id):
    grade = Grade.query.filter_by(student_id=student_id, subject_id=subject_id).first()

    if request.method == 'POST':
        grade.grade = request.form['grade']
        db.session.commit()
        return redirect(url_for('grades.grades'))

    return render_template('edit_grade.html', grade=grade)