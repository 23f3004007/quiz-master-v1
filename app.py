from flask import Flask, redirect, request, render_template, url_for, session, abort, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone, date
from functools import wraps
import json
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
    name = db.Column(db.String(150), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Interval, nullable=False, default=timedelta(hours=1))
    end_time = db.Column(db.DateTime, nullable=False)
    remarks = db.Column(db.Text)
    questions = db.relationship('Questions', backref='quiz', lazy=True)
    scores = db.relationship('Scores', backref='quiz', lazy=True)

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
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.now(IST))
    total_scored = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Interval, nullable=False)  
    user_answers = db.Column(db.Text, nullable=False)  


@app.route('/')
def home():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user and user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))  


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        return redirect(url_for('admin_dashboard' if user.is_admin else 'user_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
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
    quizzes = Quiz.query.all()
    return render_template('admin_dashboard.html', 
                         users=users, 
                         subjects=subjects,
                         chapters=chapters,
                         quizzes=quizzes)
# SUBJECT ROUTES
@app.route('/admin/subject/create', methods=['GET', 'POST'])
@admin_required
def create_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect(url_for('subject_page', subject_id=new_subject.subject_id))

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
        name = request.form['name']
        description = request.form['description']
        subject_id = request.form['subject_id']
        
        new_chapter = Chapters(name=name, description=description, subject_id=subject_id)
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


#quiz
@app.route('/admin/quiz/create', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quiz_name']
        chapter_id = request.form['chapter_id']
        date_of_quiz = request.form['date_of_quiz']
        end_time_input = request.form['end_time']  
        duration = int(request.form['duration'])
        remarks = request.form['remarks']

        start_time = datetime.strptime(date_of_quiz, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end_time_input, "%Y-%m-%dT%H:%M")

        if end_time <= start_time:
            flash("End time must be after the start time.", "danger")
            return redirect(url_for('create_quiz'))

        min_allowed_end_time = start_time + timedelta(minutes=duration + 10)
        if end_time < min_allowed_end_time:
            flash("End time must be at least 10 minutes more than the quiz duration.", "danger")
            return redirect(url_for('create_quiz'))

        new_quiz = Quiz(
            name=quiz_name,
            chapter_id=chapter_id,
            date_of_quiz=start_time,
            time_duration=timedelta(minutes=duration),
            end_time=end_time,
            remarks=remarks
        )
        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz created! Now add at least one question.', 'success')

        return redirect(url_for('create_question', quiz_id=new_quiz.quiz_id))

    chapters = Chapters.query.all()
    return render_template('create_quiz.html', chapters=chapters)


@app.route('/admin/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
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

#question
@app.route('/admin/question/create/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

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
    user = Users.query.get_or_404(user_id)

    if request.method == 'POST':
        user.fullname = request.form['fullname']
        user.email = request.form['email']
        user.qualification = request.form['qualification']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', user=user)

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


#user
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user = Users.query.get(session['user_id'])  
    subjects = Subject.query.all() 
    quizzes = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now()).order_by(Quiz.date_of_quiz).all()
    return render_template(
        'user_dashboard.html',
        user=user,
        subjects=subjects,
        quizzes=quizzes
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
    scores = Scores.query.filter_by(user_id=user.user_id).all()
    return render_template('user_quizzes.html', scores=scores)

@app.route('/user/quiz/review/<int:score_id>')
@login_required
def quiz_review(score_id):
    score = Scores.query.get_or_404(score_id)
    quiz = Quiz.query.get(score.quiz_id)
    questions = Questions.query.filter_by(quiz_id=quiz.quiz_id).all()
    user_answers = json.loads(score.user_answers) 

    return render_template('quiz_review.html', score=score, quiz=quiz, questions=questions, user_answers=user_answers)

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
        if not start_time_str:
            flash("Start time is missing. Please retry the quiz.", "danger")
            return redirect(url_for('attempt_quiz', quiz_id=quiz_id))

        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        start_time = start_time.replace(tzinfo=IST)

        end_time = datetime.now().astimezone(IST)
        time_taken = end_time - start_time
        time_taken = time_taken - timedelta(hours=5, minutes=30) 

        score = 0
        user_answers = {}

        for question in questions:
            selected_option = request.form.get(f'q{question.question_id}')
            correct_option = question.correct_option

            user_answers[str(question.question_id)] = {
                "selected": int(selected_option) if selected_option else None,
                "correct": correct_option
            }

            if selected_option and int(selected_option) == correct_option:
                score += 1

        new_score = Scores(
            user_id=session['user_id'],
            quiz_id=quiz_id,
            total_scored=score,
            time_taken=time_taken,  
            user_answers=json.dumps(user_answers)  
        )
        db.session.add(new_score)
        db.session.commit()

        flash(f'Quiz completed! Your score: {score}/{len(questions)}', 'success')
        return redirect(url_for('quiz_review', score_id=new_score.score_id))

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)


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