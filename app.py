from flask import Flask, redirect, request, render_template, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone, date
from functools import wraps

IST = timezone(timedelta(hours=5, minutes=30))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master_database.sqlite3'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = Users.query.get(session['user_id'])
        if not user or not user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship('Scores', backref='user', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subject'
    subject_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapters', backref='subject', lazy=True)

class Chapters(db.Model):
    __tablename__ = 'chapters'
    chapter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    __tablename__ = 'quiz'
    quiz_id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Interval, nullable=False, default=timedelta(hours=1))
    remarks = db.Column(db.Text)
    questions = db.relationship('Questions', backref='quiz', lazy=True)
    scores = db.relationship('Scores', backref='quiz', lazy=True)

class Questions(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Scores(db.Model):
    __tablename__ = 'scores'
    score_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.now(IST))
    total_scored = db.Column(db.Integer, nullable=False)


@app.route('/')
def home():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:  # If user is already logged in, redirect
        user = Users.query.get(session['user_id'])
        if user.is_admin:
            return redirect(url_for('admin_dash'))
        else:
            return redirect(url_for('user_dash'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id  # Store the user's ID in the session
            if user.is_admin:
                return redirect(url_for('admin_dash'))
            else:
                return redirect(url_for('user_dash'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:  # If user is already logged in, redirect
        return redirect(url_for('user_dash'))

    if request.method == 'POST':
        email = request.form['email']
        if Users.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already exists")
        
        hashed_password = generate_password_hash(request.form['password'])
        dob_date = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        
        new_user = Users(
            email=email,
            password=hashed_password,
            fullname=request.form['fullname'],
            qualification=request.form.get('qualification'),
            dob=dob_date
        )
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/admin_dash')
@login_required
@admin_required
def admin_dash():
    return render_template('admin_dash.html')

@app.route('/user_dash')
@login_required
def user_dash():
    return render_template('user_dash.html')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('home'))
def create_admin():
    with app.app_context():
        db.create_all()
        if not Users.query.filter_by(is_admin=True).first():
            admin = Users(
                email='admin@example.com',
                password=generate_password_hash('admin_password'),
                fullname="Admin User",
                dob=date.today(),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    create_admin()
    app.run(debug=True)
