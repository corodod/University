from flask import Flask, redirect, url_for, session
from flask_session import Session
from models import db
from routes.students import students_bp
from routes.grades import grades_bp
from routes.subjects import subjects_bp
from routes.auth import auth_bp  # Добавляем новый Blueprint

app = Flask(__name__)

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Настройки сессий
app.config['SECRET_KEY'] = 'your_secret_key'  # Установи сложный ключ
app.config['SESSION_TYPE'] = 'filesystem'  # Храним сессии на диске
Session(app)

# Инициализация базы данных
db.init_app(app)

# Регистрация Blueprint-ов
app.register_blueprint(auth_bp)  # Добавляем авторизацию
app.register_blueprint(students_bp)
app.register_blueprint(grades_bp)
app.register_blueprint(subjects_bp)

@app.route('/')
def index():
    # Если пользователь авторизован как админ, отправляем на students
    if session.get('user') == 'admin':
        return redirect(url_for('students.students'))
    
    # Если авторизован студент, отправляем в его личный кабинет
    elif session.get('user'):
        return redirect(url_for('auth.student_dashboard', student_id=session.get('user')))
    
    # Если не авторизован, отправляем на страницу входа
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
