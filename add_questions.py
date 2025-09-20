import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

# Function to read questions from a text file and insert them into the database
def add_questions_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    questions = []
    i = 0
    while i < len(lines):
        # Read a single question and its options
        question_text = lines[i].strip()
        option_a_line = lines[i + 1].strip()
        option_b = lines[i + 2].strip()
        option_c = lines[i + 3].strip()

        # Determine the correct answer (which ends with Y)
        option_a, correct_answer = parse_option(option_a_line)
        option_b, _ = parse_option(option_b)
        option_c, _ = parse_option(option_c)

        # Add the question to the list
        questions.append({
            'question_text': question_text,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': "_",  # Default option D as "_"
            'correct_answer': correct_answer
        })

        # Move to the next question (skip over 4 lines and the blank line)
        i += 5

    # Add the questions to the database
    with app.app_context():
        for question in questions:
            new_question = Question(
                question_text=question['question_text'],
                option_a=question['option_a'],
                option_b=question['option_b'],
                option_c=question['option_c'],
                option_d=question['option_d'],
                correct_answer=question['correct_answer']
            )
            db.session.add(new_question)

        db.session.commit()
        print(f"{len(questions)} questions added to the database.")

# Helper function to parse an option and determine if it is the correct one
def parse_option(option_line):
    """Parse a line that contains an option and check if it is marked as the correct answer."""
    if option_line.endswith(" Y"):  # Check if it ends with " Y"
        correct_answer = option_line[0]  # The first character is the option letter (A, B, C)
        option_text = option_line[:-2]  # Remove " Y" to get the option text
    else:
        correct_answer = "_"
        option_text = option_line
    return option_text, correct_answer

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    add_questions_from_file('questions.txt')
