from flask import Flask, render_template, flash, redirect, url_for, send_from_directory
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField
from wtforms.validators import DataRequired
import csv
import pandas as pd
import matplotlib.pyplot as plt
import os


app= Flask(__name__)
# Create secret key to avoid hackers for Wtf
app.config['SECRET_KEY']= "CONFIDENTIAL KEY"


# Create a form class
class NamerForm(FlaskForm):
    id_type = RadioField('ID Type', choices=[('student_id', 'Student ID'), ('course_id', 'Course ID')], validators=[DataRequired()])
    id_value = StringField('ID Value', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create namer form
@app.route('/namerform',methods=['GET','POST'],endpoint='namerform')
def form():
    form=NamerForm()
    if form.validate_on_submit():
        id_type = form.id_type.data
        id_value = form.id_value.data
        if id_type == 'student id':
            return redirect(url_for('student_details', student_id=id_value))
        elif id_type == 'course':
            return redirect(url_for('course_statistics', course_id=id_value))
        # form.id_value.data = ''
        # flash("Form submitted successfully !!! ")
    return render_template("namerform.html",form=form)

#################################
# @app.route('/student/<student_id>')
# def student_details(student_id):
#     f=open('data.csv',r)
#     data_list=f.readlines()
#     student_list=[]
#     course_list=[]
#     for each_line in data_list[1:]:
#             again_list=each_line.split(',')
#             if F_ID =='st_id' and input_Number== again_list[0].strip():
#                 student_list.append(each_line)
#             else:
#                 if F_ID == 'c_id' and input_Number== again_list[1].strip():
#                     course_list.append(each_line)
#############################


# @app.route('/')
# def index():
#     return render_template("index.html")

# @app.route('/user/<name>')
# def user(name):
#     return "<h1>Hello {}</h1>".format(name)
    


@app.route('/add/')
def add():
    first_name= "Jessica"
    # Will use safe filter in the template to remove the html tags
    # Will use striptag filter in the template to remove the html tags
    stuff= "This is a <strong>bold</strong> text "   
    stuff1= "This is a title text "   
    favorite_pizza=["pepperoni","Cheese",49]
    return render_template("user.html",first_name=first_name,stuff=stuff,stuff1=stuff1,favorite_pizza=favorite_pizza)  
    


@app.route('/users/<name>')
def users(name):
    return render_template("userprofile.html",user_name=name)


@app.errorhandler(404)
def error_page(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def error_page(e):
    return render_template("500.html"), 500

if __name__=='__main__':
    app.run(debug=True)

