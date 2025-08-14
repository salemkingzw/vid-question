import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Models
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        image = request.files['image']

        image_filename = None
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        question = Question(
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            image_filename=image_filename
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!')
        return redirect(url_for('add_question'))

    questions = Question.query.all()
    return render_template('add_question.html', questions=questions)


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    questions = Question.query.all()
    if request.method == 'POST':
        user_answers = request.form.to_dict()
        score = 0
        results = []

        for question in questions:
            user_answer = user_answers.get(str(question.id))
            correct_option_text = getattr(question, f"option_{question.correct_answer.lower()}")
            user_option_text = getattr(question, f"option_{user_answer.lower()}") if user_answer else None
            is_correct = user_answer == question.correct_answer
            if is_correct:
                score += 1
            results.append({
                'question': question,
                'user_answer': user_option_text,
                'correct_answer': correct_option_text,
                'is_correct': is_correct
            })

        return render_template('result.html', results=results, score=score, total=len(questions))

    return render_template('quiz.html', questions=questions)

@app.route('/delete_question/<int:id>', methods=['POST'])
def delete_question(id):
    question = Question.query.get_or_404(id)

    # If the question has an associated image, delete the file
    if question.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], question.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!')
    return redirect(url_for('add_question'))

@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    question = Question.query.get_or_404(id)

    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        image = request.files['image']

        # Update question details
        question.question_text = question_text
        question.option_a = option_a
        question.option_b = option_b
        question.option_c = option_c
        question.option_d = option_d
        question.correct_answer = correct_answer

        # If a new image is uploaded, replace the old one
        if image and image.filename != '':
            # Delete the old image if it exists
            if question.image_filename:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], question.image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Save the new image
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            question.image_filename = image_filename

        db.session.commit()
        flash('Question updated successfully!')
        return redirect(url_for('add_question'))

    return render_template('edit_question.html', question=question)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)