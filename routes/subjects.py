from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Subject, Faculty

subjects_bp = Blueprint('subjects', __name__)


@subjects_bp.route('/subjects', methods=['GET', 'POST'])
def subjects():
    faculties = Faculty.query.all()
    faculty_id = request.args.get('faculty')

    page = request.args.get('page', 1, type=int)
    per_page = 10

    subjects_query = Subject.query
    if faculty_id:
        subjects_query = subjects_query.filter_by(faculty_id=faculty_id)

    subjects = subjects_query.paginate(page=page, per_page=per_page)

    # Подсчет общего количества предметов (учитывая выбранный факультет)
    total_subjects = subjects_query.count()

    return render_template(
        'subjects.html',
        subjects=subjects.items,
        faculties=faculties,
        selected_faculty=faculty_id,
        page=page,
        total_pages=subjects.pages,
        total_subjects=total_subjects  # Передаем общее число предметов
    )


@subjects_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get(subject_id)

    if request.method == 'POST':
        subject.subject_name = request.form['subject_name']
        subject.hours = request.form['hours']
        db.session.commit()
        return redirect(url_for('subjects.subjects', faculty=subject.faculty_id))

    return render_template('edit_subject.html', subject=subject)

@subjects_bp.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    Grade.query.filter_by(subject_id=subject_id).delete()
    subject = Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('subjects.subjects', faculty=subject.faculty_id))