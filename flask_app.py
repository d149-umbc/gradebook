
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)

"""
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
"""

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    studentid = db.Column(db.String(128))
    major = db.Column(db.String(128))
    email = db.Column(db.String(128))


class Assignment(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    maxscore = db.Column(db.Integer)
    date = db.Column(db.DateTime)

class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    assignmentid = db.Column(db.Integer)
    studentid = db.Column(db.Integer)
    score = db.Column(db.Integer)





app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="d149",
    password="mysqlpythonanywhere",
    hostname="d149.mysql.pythonanywhere-services.com",
    databasename="d149$gradebook",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False






@app.route('/')
def gradebook():
    students = Student.query.order_by(Student.lastname).all()
    assignments = Assignment.query.order_by(Assignment.date).all()
    scores = Score.query.all()
    table = {}
    namelookup = { }
    for s in students:
        table[int(s.id)] = {}
        namelookup[int(s.id)] = str(s.lastname) + ", "+ str(s.firstname)
        for a in assignments:
            table[int(s.id)][int(a.id)] = "-"
    for s in scores:
        table[int(s.studentid)][int(s.assignmentid)] = int(s.score)
    #return "hello world"
    return render_template('gradebook.html',students=students, table=table, assignments=assignments, namelookup = namelookup)


@app.route('/scoreedit/<student>/<assignment>', methods=["GET", "POST"])
def scoreedit(student, assignment):
    if request.method == "GET":
        return render_template("scoreedit.html",s=student,a=assignment)
    score = request.form['score']
    # check for existing
    exist = Score.query.filter_by(assignmentid = assignment, studentid = student).first()
    if exist:
        db.session.delete(exist)
        db.session.commit()

    result = Score(assignmentid = assignment, studentid = student, score = score)
    db.session.add(result)
    db.session.commit()
    return redirect(url_for('gradebook'))

@app.route('/student/add', methods=["GET", "POST"])
def add_student():
        if request.method == "GET":
            return render_template("studentadd.html")

        elif request.method == "POST":
            fn = request.form['firstname']
            addme = Student(firstname = fn, lastname = request.form["lastname"], studentid = request.form["studentid"], major = request.form["major"], email = request.form["email"] )
            db.session.add(addme)
            db.session.commit()
            return redirect(url_for('gradebook'))
            #return fn




"""
@app.route('/comments', methods=["GET", "POST"])
def comments_handler():
    if request.method == "GET":
        return render_template("comments.html", comments=Comment.query.all())

    comment = Comment(content=request.form["contents"])
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('comments_handler'))
"""