from flask import Flask, render_template, request, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

class Student:
    def __init__(self, name, roll_number):
        self.name = name
        self.roll_number = roll_number
        self.grades = {}

    def add_grade(self, subject, grade):
        if 0 <= grade <= 100:
            self.grades[subject] = grade

    def calculate_average(self):
        if not self.grades:
            return 0
        return sum(self.grades.values()) / len(self.grades)

class StudentTracker:
    def __init__(self):
        self.students = {}

    def add_student(self, name, roll_number):
        if roll_number not in self.students:
            self.students[roll_number] = Student(name, roll_number)

    def add_grade(self, roll_number, subject, grade):
        if roll_number in self.students:
            self.students[roll_number].add_grade(subject, grade)

    def view_student_details(self, roll_number):
        if roll_number in self.students:
            return self.students[roll_number]
        return None

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump({roll: student.__dict__ for roll, student in self.students.items()}, f)

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                for roll, student_data in data.items():
                    student = Student(student_data['name'], student_data['roll_number'])
                    student.grades = student_data['grades']
                    self.students[roll] = student
        except FileNotFoundError:
            pass

tracker = StudentTracker()
tracker.load_from_file('students.json')

@app.route('/')
def index():
    return render_template('index.html', students=tracker.students)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    roll_number = request.form['roll_number']
    tracker.add_student(name, roll_number)
    tracker.save_to_file('students.json')
    flash('Student added successfully!')
    return redirect(url_for('index'))

@app.route('/add_grade/<roll_number>', methods=['POST'])
def add_grade(roll_number):
    subject = request.form['subject']
    grade = float(request.form['grade'])
    tracker.add_grade(roll_number, subject, grade)
    tracker.save_to_file('students.json')
    flash('Grade added successfully!')
    return redirect(url_for('index'))

@app.route('/student/<roll_number>')
def student_details(roll_number):
    student = tracker.view_student_details(roll_number)
    return render_template('student_details.html', student=student)

if __name__ == '__main__':
    app.run(debug=True)
