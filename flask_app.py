
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from statistics import mean, median

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
    username="brentdavis771",
    password="mysqlpythonanywhere",
    hostname="brentdavis771.mysql.pythonanywhere-services.com",
    databasename="brentdavis771$gradebook",
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

@app.route('/student/delete', methods=["GET", "POST"])
def delete_student():
        if request.method == "GET":
            students = Student.query.order_by(Student.lastname).all()
            return render_template("studentdelete.html", students = students)
        elif request.method == "POST":
            studid = int(request.form['sid'])
            sid = Student.query.filter_by(id= studid).first()
            db.session.delete(sid)
            db.session.commit()
            db.session.query(Score).filter_by(studentid = studid).delete()
            #scorewipe = Score.query.filter_by(studentid = sid).all()
            #db.session.delete(scorewipe)
            db.session.commit()
            return redirect(url_for('gradebook'))

@app.route('/assignment/add', methods=["GET", "POST"])
def add_assignment():
        if request.method == "GET":
            return render_template("assignmentadd.html")

        elif request.method == "POST":
            fn = request.form['name']
            addme = Assignment(name = fn, maxscore = request.form["maxscore"], date = request.form["date"] )
            db.session.add(addme)
            db.session.commit()
            return redirect(url_for('gradebook'))



@app.route('/assignment/delete', methods=["GET", "POST"])
def delete_assignment():
        if request.method == "GET":
            assignments = Assignment.query.order_by(Assignment.name).all()
            return render_template("assignmentdelete.html", assignments = assignments)
        elif request.method == "POST":
            asid = int(request.form['aid'])
            aid = Assignment.query.filter_by(id= asid).first()
            db.session.delete(aid)
            db.session.commit()
            db.session.query(Score).filter_by(assignmentid = asid).delete()
            #scorewipe = Score.query.filter_by(assignmentid = aid).all()
            #db.session.delete(scorewipe)
            db.session.commit()
            return redirect(url_for('gradebook'))

@app.route('/report/roster')
def class_roster():
        students = Student.query.order_by(Student.lastname).all()
        return render_template("reportroster.html", students = students)





@app.route('/report/student', methods=["GET", "POST"])
def report_student():
        if request.method == "GET":
            students = Student.query.order_by(Student.lastname).all()
            return render_template("reportstudent.html", students = students)
        elif request.method == "POST":
            studid = int(request.form['sid'])
            sid = Student.query.filter_by(id= studid).first()
            assignments = Assignment.query.order_by(Assignment.date).all()
            scores = Score.query.filter_by(studentid = sid.id).all()


            scoretable = {}
            for a in assignments:
                scoretable[a.id]  = {"name":a.name, "maxscore": a.maxscore, "date":a.date, "score":"-", "percent":"-"}

            totalpts = 0
            assigns = 0
            for s in scores:
                scoretable[s.assignmentid]["score"]  = s.score
                scoretable[s.assignmentid]["percent"]  = s.score/ scoretable[s.assignmentid]["maxscore"] * 100
                totalpts += scoretable[s.assignmentid]["percent"]
                assigns +=1

            if assigns > 0:
                average = (totalpts / assigns)
            else:
                average = "-"

            return render_template("reportstudentview.html", student = sid, scoretable=scoretable, average=average)


@app.route('/report/assignments', methods=["GET"])
def report_assignments():
    avgtable = { }
    assignments = Assignment.query.order_by(Assignment.date).all()
    for a in assignments:
        avgrow = { "name":a.name, "date":a.date, "maxscore": a.maxscore, "min": 10000, "max":0, "average":"-", "median":"-"}
        scores = scores = Score.query.filter_by(assignmentid = a.id).all()
        pv = []
        for s in scores:
            if s.score < avgrow["min"]:
                avgrow["min"] = s.score
            if s.score > avgrow["max"]:
                avgrow["max"] = s.score

            pv.append(s.score)
        if len(pv) > 0:
            avgrow["average"] = mean(pv)
            avgrow["median"] = median(pv)
        else:
            avgrow["min"] = "-"
            avgrow["max"] = "-"


        avgrow["n"] = len(pv)
        avgtable[a.id] = avgrow

    return render_template("reportassignments.html", avgtable = avgtable)


@app.route('/report/averages')
def report_averages():
    students = Student.query.order_by(Student.lastname).all()
    result = {}
    for s in students:
            #copied mostly from indivdual student report -- should be a method/function
            assignments = Assignment.query.order_by(Assignment.date).all()
            maxpointlist = { }
            for a in assignments:
                maxpointlist[a.id] = a.maxscore


            scores = Score.query.filter_by(studentid = s.id).all()
            scorelist = []
            for score in scores:
                scorelist.append(score.score / maxpointlist[score.assignmentid])

            avg = "-"
            if len(scorelist) > 0:
                avg=round((mean(scorelist) *100), 2)


            result[s.id] = {"lastname": s.lastname, "firstname": s.firstname, "average": avg}

    return render_template("reportaverages.html", result = result)














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