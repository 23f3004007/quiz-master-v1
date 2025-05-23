from flask import Flask, redirect, request, render_template, url_for, session, abort, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone, date
from functools import wraps
import json
from datetime import timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master_database.sqlite3'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.endpoint in ["login", "register"]:  
                return f(*args, **kwargs)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.endpoint == "login":  
                return f(*args, **kwargs)
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            flash("Unauthorized access!", "danger")
            return redirect(url_for('user_dashboard'))  

        return f(*args, **kwargs)
    return decorated_function



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
    chapters = db.relationship('Chapters', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapters(db.Model):
    __tablename__ = 'chapters'
    chapter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__ = 'quiz'
    quiz_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Interval, nullable=False, default=timedelta(hours=1))
    end_time = db.Column(db.DateTime, nullable=False)
    remarks = db.Column(db.Text)
    questions = db.relationship('Questions', backref='quiz', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('Scores', backref='quiz', lazy=True,cascade='all, delete-orphan')

class Questions(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
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
    time_stamp_of_attempt = db.Column(db.Integer, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  
    user_answers = db.Column(db.Text, nullable=False)  


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard' if session.get('role') == 'admin' else 'user_dashboard'))
    return render_template('homepage.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        target_dashboard = 'admin_dashboard' if user.is_admin else 'user_dashboard'
        if request.endpoint == target_dashboard:  # Prevent redirect loop
            return render_template('login.html')
        return redirect(url_for(target_dashboard))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['role'] = 'admin' if user.is_admin else 'user'
            return redirect(url_for('admin_dashboard' if user.is_admin else 'user_dashboard'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user_dash'))

    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        fullname = request.form['fullname']
        qualification = request.form['qualification']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        
        new_user = Users(
            email=email,
            password=password,
            fullname=fullname,
            qualification=qualification,
            dob=dob
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = Users.query.all()
    subjects = Subject.query.all()
    chapters = Chapters.query.all()
    # Eagerly load the relationships
    quizzes = Quiz.query.join(Chapters).join(Subject).all()
    
    return render_template('admin_dashboard.html', 
                         users=users, 
                         subjects=subjects,
                         chapters=chapters,
                         quizzes=quizzes)
    
@app.route('/admin/summary')
@admin_required
def admin_summary():
    quizzes = Quiz.query.all()
    users = Users.query.all()
    total_quizzes = len(quizzes)

    total_participants = 0
    overall_total_score = 0
    overall_attempts = 0
    quiz_summaries = []
    user_summaries = []
    quiz_labels = []
    quiz_avg_scores = []
    user_labels = []
    user_avg_scores = []
    for quiz in quizzes:
        attempts = Scores.query.filter_by(quiz_id=quiz.quiz_id).count()
        total_score = db.session.query(db.func.sum(Scores.total_scored)).filter(Scores.quiz_id == quiz.quiz_id).scalar() or 0
        avg_score = total_score / attempts if attempts > 0 else 0
        
        quiz_summaries.append({
            "name": quiz.name,
            "attempts": attempts,
            "avg_score": avg_score
        })
        quiz_labels.append(quiz.name)
        quiz_avg_scores.append(avg_score)

    for user in users:
        user_attempts = Scores.query.filter_by(user_id=user.user_id).count()
        user_total_score = db.session.query(db.func.sum(Scores.total_scored)).filter(Scores.user_id == user.user_id).scalar() or 0
        user_avg_score = user_total_score / user_attempts if user_attempts > 0 else 0
        
        if user_attempts > 0:
            total_participants += 1
            overall_total_score += user_total_score
            overall_attempts += user_attempts

            user_summaries.append({
                "fullname": user.fullname,
                "email": user.email,
                "total_attempts": user_attempts,
                "avg_score": user_avg_score
            })

            
            user_labels.append(user.fullname)
            user_avg_scores.append(user_avg_score)

    overall_avg_score = overall_total_score / overall_attempts if overall_attempts > 0 else 0

    return render_template('admin_summary.html', 
        total_quizzes=total_quizzes, 
        total_participants=total_participants, 
        overall_avg_score=overall_avg_score, 
        quiz_summaries=quiz_summaries, 
        user_summaries=user_summaries,
        quiz_labels=quiz_labels, 
        quiz_avg_scores=quiz_avg_scores,
        user_labels=user_labels, 
        user_avg_scores=user_avg_scores
    )


    
    
@app.route('/admin/manage_subjects')
@admin_required
def manage_subjects():
    subjects = Subject.query.all()
    return render_template('manage_subjects.html', subjects=subjects)

@app.route('/admin/manage_quizzes')
@admin_required
def manage_quizzes():
    quizzes = Quiz.query.all()
    return render_template('manage_quizzes.html', quizzes=quizzes)

# SUBJECT ROUTES
@app.route('/admin/subject/create', methods=['GET', 'POST'])
@admin_required
def create_subject():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name or len(name) < 3:
            flash("Subject name must be at least 3 characters.", "danger")
            return redirect(url_for('create_subject'))
        if Subject.query.filter_by(name=name).first():
            flash("Subject already exists!", "danger")
            return redirect(url_for('create_subject'))

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_subject.html')


@app.route('/admin/subject/edit/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('subject_page', subject_id=subject.subject_id))

    return render_template('edit_subject.html', subject=subject)

@app.route('/admin/subject/delete/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id) 
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# CHAPTER ROUTES
@app.route('/admin/chapter/create', methods=['GET', 'POST'])
@admin_required
def create_chapter():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        subject_id = request.form.get('subject_id')

        if not name or len(name) < 3:
            flash("Chapter name must be at least 3 characters.", "danger")
            return redirect(url_for('create_chapter'))

        if not Subject.query.get(subject_id):
            flash("Invalid subject selected.", "danger")
            return redirect(url_for('create_chapter'))

        new_chapter = Chapters(name=name, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('subject_page', subject_id=subject_id))

    subjects = Subject.query.all()
    return render_template('create_chapter.html', subjects=subjects)


@app.route('/admin/chapter/edit/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapters.query.get_or_404(chapter_id)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        chapter.subject_id = request.form['subject_id']
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('subject_page', subject_id=chapter.subject_id))

    subjects = Subject.query.all() 
    return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)

@app.route('/admin/chapter/delete/<int:chapter_id>', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapters.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id  
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('subject_page', subject_id=subject_id))


#quiz routes
@app.route('/admin/quiz/create', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form.get('quiz_name', '').strip()
        chapter_id = request.form.get('chapter_id')
        date_of_quiz = request.form.get('date_of_quiz')
        end_time = request.form.get('end_time')
        duration = int(request.form.get('duration', 0))
        remarks = request.form.get('remarks', '').strip()

        if not quiz_name or len(quiz_name) < 3:
            flash("Quiz name must be at least 3 characters.", "danger")
            return redirect(url_for('create_quiz'))

        try:
            start_time = datetime.strptime(date_of_quiz, "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
            if end_time <= start_time + timedelta(minutes=duration):
                flash("End time must be greater than the quiz duration.", "danger")
                return redirect(url_for('create_quiz'))
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for('create_quiz'))

        # Create the quiz first
        new_quiz = Quiz(
            name=quiz_name,
            chapter_id=chapter_id,
            date_of_quiz=start_time,
            end_time=end_time,
            time_duration=timedelta(minutes=duration),
            remarks=remarks
        )
        db.session.add(new_quiz)
        db.session.commit()

        # Now check for questions and redirect accordingly
        if Questions.query.filter_by(chapter_id=chapter_id).count() == 0:
            flash("Please add at least one question to the quiz.", "warning")
            return redirect(url_for('create_question', quiz_id=new_quiz.quiz_id))

        flash('Quiz created successfully!', 'success')
        return redirect(url_for('quiz_page', quiz_id=new_quiz.quiz_id))

    chapters = Chapters.query.all()
    return render_template('create_quiz.html', chapters=chapters)



@app.route('/admin/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        quiz.name = request.form['quiz_name']
        quiz.chapter_id = request.form['chapter_id']
        quiz.date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%dT%H:%M')
        quiz.time_duration = timedelta(minutes=int(request.form['duration']))
        quiz.remarks = request.form['remarks']
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    chapters = Chapters.query.all()
    return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

@app.route('/admin/quiz/delete/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

#question routes
@app.route('/admin/question/create/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def create_question(quiz_id):
    # Load quiz with chapter relationship
    quiz = Quiz.query.join(Chapters).filter(Quiz.quiz_id == quiz_id).first_or_404()
    
    if request.method == 'POST':
        question_text = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']

        new_question = Questions(
            question_statement=question_text,
            option_1=option1,
            option_2=option2,
            option_3=option3,
            option_4=option4,
            correct_option=correct_option,
            quiz_id=quiz_id,
            chapter_id=quiz.chapter_id
        )
        db.session.add(new_question)
        db.session.commit()

        flash('Question added successfully!', 'success')
        
        # Check if there are enough questions
        question_count = Questions.query.filter_by(quiz_id=quiz_id).count()
        if question_count >= 5:  # Minimum 5 questions required
            return redirect(url_for('subject_page', subject_id=quiz.chapter.subject_id))
        else:
            flash(f'Please add more questions. Currently {question_count}/5 questions.', 'info')
            return redirect(url_for('create_question', quiz_id=quiz_id))

    return render_template('create_question.html', quiz=quiz)


@app.route('/admin/question/edit/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Questions.query.get_or_404(question_id)
    if request.method == 'POST':
        question.question_statement = request.form['question']
        question.option_1 = request.form['option1']
        question.option_2 = request.form['option2']
        question.option_3 = request.form['option3']
        question.option_4 = request.form['option4']
        question.correct_option = int(request.form['correct_option'])
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('edit_quiz', quiz_id=question.quiz_id))
    return render_template('edit_question.html', question=question)

@app.route('/admin/question/delete/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = Questions.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('edit_quiz', quiz_id=quiz_id))

@app.route('/admin/users')
@admin_required
def manage_users():
    users = Users.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    profile_user = Users.query.get_or_404(user_id)
    current_user = Users.query.get(session['user_id'])

    if request.method == 'POST':
        profile_user.fullname = request.form['fullname']
        profile_user.email = request.form['email']
        profile_user.qualification = request.form['qualification']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', 
                         profile_user=profile_user,
                         current_user=current_user)

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))


@app.route('/admin/search', methods=['GET'])
@login_required
@admin_required
def admin_search():
    query = request.args.get('q', '').strip().lower()
    users = Users.query.filter(
        (Users.fullname.ilike(f"%{query}%")) | 
        (Users.email.ilike(f"%{query}%"))
    ).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    questions = Questions.query.filter(Questions.question_statement.ilike(f"%{query}%")).all()

    return render_template(
        'admin_search_results.html',
        query=query,
        users=users,
        subjects=subjects,
        quizzes=quizzes,
        questions=questions
    )

@app.route('/subject/<int:subject_id>')
@login_required
def subject_page(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapters.query.filter_by(subject_id=subject_id).all()
    quizzes = Quiz.query.join(Chapters).filter(Chapters.subject_id == subject_id).all()
    user = Users.query.get(session['user_id']) 

    return render_template('subject_page.html', subject=subject, chapters=chapters, quizzes=quizzes, user=user)


@app.route('/quiz/<int:quiz_id>')
@login_required
def quiz_page(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user = Users.query.get(session['user_id'])
    return render_template('quiz_page.html', quiz=quiz,user=user)


#user routes
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user = Users.query.get(session['user_id'])  
    subjects = Subject.query.all() 
    quizzes = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now()).order_by(Quiz.date_of_quiz).all()
    scores = Scores.query.filter_by(user_id=user.user_id).all()
    quiz_names = [s.quiz.name for s in scores]
    quiz_scores = [s.total_scored for s in scores]
    return render_template(
        'user_dashboard.html',
        user=user,
        subjects=subjects,
        quizzes=quizzes,
        quiz_names=quiz_names, 
        quiz_scores=quiz_scores
    )


@app.route('/user/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    profile_user = Users.query.get_or_404(user_id)
    current_user = Users.query.get(session['user_id'])

    return render_template(
        'user_profile.html',
        profile_user=profile_user,
        current_user=current_user
    )


@app.route('/user/quizzes')
@login_required
def user_quizzes():
    user = Users.query.get(session['user_id'])
    scores = Scores.query.filter_by(user_id=user.user_id).order_by(Scores.time_stamp_of_attempt.desc()).all()
    return render_template('user_quizzes.html', 
                         scores=scores, 
                         datetime=datetime,
                         IST=IST)  # Pass IST timezone

@app.route('/user/quiz/review/<int:score_id>')
@login_required
def quiz_review(score_id):
    score = Scores.query.get_or_404(score_id)
    
    # Get the start time from time_stamp_of_attempt
    attempt_time = datetime.fromtimestamp(score.time_stamp_of_attempt, tz=timezone.utc)
    attempt_time_ist = attempt_time.astimezone(IST)
    
    # Format time taken
    minutes, seconds = divmod(score.time_taken, 60)
    hours, minutes = divmod(minutes, 60)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    quiz = Quiz.query.get(score.quiz_id)
    questions = Questions.query.filter_by(quiz_id=quiz.quiz_id).all()
    user_answers = json.loads(score.user_answers)

    # Convert user_answers to the expected format if needed
    formatted_answers = {}
    for q_id, answer in user_answers.items():
        formatted_answers[q_id] = {
            'selected': int(answer) if isinstance(answer, (str, int)) else None
        }

    return render_template('quiz_review.html', 
                         score=score, 
                         quiz=quiz, 
                         questions=questions, 
                         user_answers=formatted_answers,
                         formatted_time=formatted_time,
                         attempt_time=attempt_time_ist)

@app.route('/user/search', methods=['GET'])
@login_required
def user_search():
    query = request.args.get('q', '').strip().lower() 
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    subject_ids = [subject.subject_id for subject in subjects]
    quizzes_in_subjects = Quiz.query.join(Chapters).filter(Chapters.subject_id.in_(subject_ids)).all()
    quizzes_by_name = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    all_quizzes = {quiz.quiz_id: quiz for quiz in (quizzes_in_subjects + quizzes_by_name)}.values()
    quizzes_under_subjects = {quiz.quiz_id: quiz for quiz in quizzes_in_subjects}
    other_quizzes = [quiz for quiz in all_quizzes if quiz.quiz_id not in quizzes_under_subjects]

    return render_template(
        'user_search_results.html',
        query=query,
        subjects=subjects,
        quizzes_under_subjects=quizzes_under_subjects.values(),
        other_quizzes=other_quizzes
    )



@app.route('/user/quiz/attempt/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Questions.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        start_time_str = request.form.get('start_time')
        time_taken = int(request.form.get('time_taken', 0))
        
        # Process answers
        user_answers = {}
        score = 0
        
        for question in questions:
            answer_key = f'question_{question.question_id}'
            selected_answer = request.form.get(answer_key)
            
            if selected_answer:
                user_answers[str(question.question_id)] = int(selected_answer)
                if int(selected_answer) == question.correct_option:
                    score += 1

        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%f')
            
            new_score = Scores(
                user_id=session['user_id'],
                quiz_id=quiz_id,
                time_stamp_of_attempt=int(datetime.now().timestamp()),
                total_scored=score,
                time_taken=time_taken,
                user_answers=json.dumps(user_answers)
            )
            db.session.add(new_score)
            db.session.commit()

            flash(f'Quiz completed! Your score: {score}/{len(questions)}', 'success')
            return redirect(url_for('quiz_review', score_id=new_score.score_id))
            
        except ValueError as e:
            flash('Error submitting quiz. Please try again.', 'danger')
            return redirect(url_for('attempt_quiz', quiz_id=quiz_id))

    # Add current time for GET requests
    start_time = datetime.now()
    return render_template('attempt_quiz.html', 
                         quiz=quiz, 
                         questions=questions,
                         start_time=start_time)


@app.route('/user/available-quizzes')
@login_required
def available_quizzes():
    subjects = Subject.query.all() 
    quizzes = Quiz.query.all() 
    return render_template('available_quizzes.html', subjects=subjects, quizzes=quizzes)


@app.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        user = Users.query.get(session['user_id'])
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        
        if check_password_hash(user.password, current_password):
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('user_profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('change_password.html')

@app.route('/user/quiz/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Questions.query.filter_by(quiz_id=quiz_id).all()
    return render_template('view_quiz.html', quiz=quiz, questions=questions)


#API ROUTES
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    subjects_list = [{"id": s.subject_id, "name": s.name, "description": s.description} for s in subjects]
    return jsonify(subjects_list) 

@app.route('/api/chapters/<int:subject_id>', methods=['GET'])
def get_chapters(subject_id):
    chapters = Chapters.query.filter_by(subject_id=subject_id).all()
    chapters_list = [{"id": c.chapter_id, "name": c.name, "description": c.description} for c in chapters]
    return jsonify(chapters_list)

@app.route('/api/quizzes/<int:chapter_id>', methods=['GET'])
def get_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    quizzes_list = [{"id": q.quiz_id, "name": q.name, "date": q.date_of_quiz.strftime('%Y-%m-%d %H:%M'), "remarks": q.remarks} for q in quizzes]
    return jsonify(quizzes_list)

@app.route('/api/scores/<int:user_id>', methods=['GET'])
def get_scores(user_id):
    scores = Scores.query.filter_by(user_id=user_id).all()
    scores_list = [{"id": s.score_id, "quiz_id": s.quiz_id, "total_score": s.total_scored, "attempt_date": s.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M')} for s in scores]
    return jsonify(scores_list)



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

if __name__ == '__main__':
    create_admin()
    app.run(debug=True)