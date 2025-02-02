from flask import Flask, redirect, request, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta,timezone


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master_database.sqlite3'
app.config['SECRET_KEY']='secret_key'
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'
    user_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    email=db.Column(db.String(120),unique=True, nullable=False)
    password=db.Column(db.String, nullable=False)
    fullname=db.Column(db.String, nullable=False)
    qualification=db.Column(db.String, nullable=True)
    dob=db.Column(db.Date, nullable=False)
    is_admin=db.Column(db.Boolean, default=False)
    scores=db.relationship('Scores',backref='user',lazy=True)

class Subject(db.Model):
    __tablename__ = 'subject'
    subject_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    description=db.Column(db.Text, nullable=True)
    chapters=db.relationship('Chapters',backref='subject',lazy=True)

class Chapters(db.Model):
    __tablename__='chapters'
    chapter_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    description=db.Column(db.Text, nullable=True)
    subject_id=db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    quizzes=db.relationship('Quiz',backref='chapters',lazy=True)

class Quiz(db.Model):
    __tablename__='quiz'
    quiz_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    chapter_id=db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    date_of_quiz=db.Column(db.DateTime, nullable=False)
    time_duration=db.Column(db.Time, nullable=False, default=timedelta(hours=1))
    remarks=db.Column(db.Text)
    questions=db.relationship('Questions',backref='quiz',lazy=True)
    scores=db.relationship('Scores',backref='quiz',lazy=True)

class Questions(db.Model):
    __tablename__='questions'
    question_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    quiz_id=db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    question_statement=db.Column(db.Text, nullable=False)
    option_1=db.Column(db.String(255), nullable=False)
    option_2=db.Column(db.String(255), nullable=False)
    option_3=db.Column(db.String(255), nullable=False)
    option_4=db.Column(db.String(255), nullable=False)
    correct_option=db.Column(db.Integer, nullable=False)

class Scores(db.Model):
    __tablename__='scores'
    scores_id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.user_id'),nullable=False)
    quiz_id=db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    chapter_id=db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    time_stamp_of_attempt=db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    total_scored=db.Column(db.Integer, nullable=False)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            session['user_id'] = user.user_id
            if user.is_admin:
                return redirect(url_for('admin_dash'))
            else:
                return redirect(url_for('user_dash'))
    return render_template('login.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password=generate_password_hash(request.form['password'])
        new_user = Users(
            email=request.form['email'],
            password=hashed_password,
            fullname=request.form['fullname'],
            qualification=request.form['qualification'],
            dob=datetime.striptime(request.form['dob'],'%Y-%m-%d')
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/admin_dash')
def admin_dash():
    return render_template('admin_dash.html')
@app.route('/user_dash')
def user_dash():
    return render_template('user_dash.html')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin=Users.query.filter_by(is_admin=True).first()
        if not admin:
            admin_password=generate_password_hash('admin_password')
            admin=Users(email='admin@example.com',
                        password=admin_password,
                        fullname="Admin User",
                        dob = datetime.now(),
                        is_admin=True)
            db.session.add(admin)
            db.session.commit()
        app.run(debug=True)