from sqlite3 import IntegrityError

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app=Flask(__name__)
app.secret_key = "my-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Mcc.db"
app.config["UPLOAD_FOLDER"]="static/upload"

db=SQLAlchemy(app)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    age=db.Column(db.Integer)
    dob=db.Column(db.Date,nullable=False)
    email=db.Column(db.String(50), unique=True, nullable=False)
    course=db.Column(db.String(30),nullable=True)
    photo=db.Column(db.String(30),nullable=True)

with app.app_context():
    db.create_all()



@app.route("/")
def home():
    students = Students.query.all()
    return render_template("index.html",students=students)

@app.route("/add_stud",methods=["GET","POST"])
def add_stud():
    if request.method=="POST":
        id=request.form.get("id")
        name=request.form.get("name")
        age=request.form.get("age")
        dob=request.form.get("dob")
        dob = datetime.strptime(dob,"%Y-%m-%d").date()
        email=request.form.get("email")
        course=request.form.get("course")

        existing_id=Students.query.filter_by(id=id).first()
        if existing_id:
            flash("Student Id Is Already Exists.","error")
            return redirect(url_for("add_stud"))
        
        existing_email=Students.query.filter_by(email=email).first()
        if existing_email:
            flash("Student Email Is Already Exists.","error")
            return redirect(url_for("add_stud"))

        photo=request.files["photo"]
        photo_path=os.path.join(app.config["UPLOAD_FOLDER"],photo.filename)
        photo.save(photo_path)

        student=Students(
            id=id,
            name=name,
            age=age,
            email=email,
            dob=dob,
            course=course,
            photo=photo.filename
        )
        db.session.add(student)
        db.session.commit()

        flash("Student added successfully!", "success")

        return redirect(url_for("home"))
    

    return render_template("add_stud.html")



@app.route("/update_stud/<int:stud_id>", methods=["GET","POST"])
def update_stud(stud_id):
    student=Students.query.get(stud_id)

    if request.method=="POST":
        student.id=request.form.get("id")
        student.name=request.form.get("name")
        student.age=request.form.get("age")
        dob=request.form.get("dob")
        student.dob = datetime.strptime(dob,"%Y-%m-%d").date()
        student.email=request.form.get("email")
        student.course=request.form.get("course")
        photo = request.files.get("photo")

        if photo and photo.filename:
            photo_path=os.path.join(app.config["UPLOAD_FOLDER"],photo.filename)
            photo.save(photo_path)
            student.photo=photo.filename

        db.session.commit()

        flash("Student updated successfully!", "success")

        return redirect(url_for("home"))
    return render_template("update_stud.html",student=student)


@app.route("/delete_stud/<int:stud_id>", methods=["GET","POST"])
def delete_stud(stud_id):
    student=Students.query.get(stud_id)
    db.session.delete(student)
    db.session.commit()

    flash("Student deleted successfully!", "success")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)