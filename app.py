from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

# Configure MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1111@localhost/studentdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---- Model (Custom DocType: Student) ----
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)

# ---- Create Database Table ----
# with app.app_context():
#     db.create_all()

# ---- Routes ----
# @app.route('/')
# def index():
#     students = Student.query.all()
#     return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        course = request.form['course']

        new_student = Student(name=name, age=age, email=email, course=course)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.age = request.form['age']
        student.email = request.form['email']
        student.course = request.form['course']
        db.session.commit()
        flash('Student updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_student.html', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!')
    return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
    total_students = db.session.execute(text("SELECT COUNT(*) FROM student")).scalar()
    course_data = db.session.execute(text("SELECT course, COUNT(*) FROM student GROUP BY course")).fetchall()
    avg_age = db.session.execute(text("SELECT AVG(age) FROM student")).scalar()
    
    return render_template(
        "dashboard.html",
        total_students=total_students,
        course_data=course_data,
        avg_age=round(avg_age, 2)
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        students = Student.query.filter(Student.name.like(f"%{keyword}%")).all()
    else:
        students = Student.query.all()

    page = request.args.get('page', 1, type=int)
    students = Student.query.paginate(page=page, per_page=5)

    return render_template('index.html', students=students)


    

if __name__ == '__main__':
    app.run(debug=True)