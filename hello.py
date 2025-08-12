from flask import Flask, render_template, flash, redirect, url_for, send_from_directory
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField
from wtforms.validators import DataRequired
import csv
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import os
import logging

    
app= Flask(__name__)
# Create secret key to avoid hackers for Wtf
app.config['SECRET_KEY']= "CONFIDENTIAL KEY"

# Create a form class
class NamerForm(FlaskForm):
    id_type = RadioField('', choices=[('student', 'Student id'), ('course', 'Course id')], validators=[DataRequired()])
    id_value = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create namer form
@app.route('/namerform', methods=['GET','POST'], endpoint='namerform')
def form():
    form = NamerForm()
    if form.validate_on_submit():
        id_type = form.id_type.data
        id_value = form.id_value.data
        
        # Match the values to your choices
        if id_type == 'student':
            return redirect(url_for('student_details', student_id=id_value))
        elif id_type == 'course':
            return redirect(url_for('course_statistics', course_id=id_value))
    
    return render_template("namerform.html", form=form)


CSV_PATH = 'data.csv'  # Make sure this is in the same directory

@app.route('/student/<student_id>')
def student_details(student_id):
    try:
        # Read CSV with proper column names
        df = pd.read_csv(CSV_PATH)
        df.columns = df.columns.str.strip()
        # Convert to integer for comparison
        student_id_int = int(student_id)
        student_data = df[df['Student id'] == student_id_int]  #Keep with spaces
        
        if student_data.empty:
            flash(f'No data found for Student ID: {student_id}', 'warning')
            return redirect(url_for('namerform'))
        
        # Calculate total marks
        total_marks = student_data['Marks'].sum()
        
        # Convert to list of dictionaries for template
        records = student_data.to_dict('records')
        
        return render_template('studentid.html',records=records,total_marks=total_marks,student_id=student_id)
    except Exception as e:
        flash(f'Error processing student data: {str(e)}', 'danger')
        return redirect(url_for('namerform'))


@app.route('/course/<course_id>')
def course_statistics(course_id):
    try:
        # Read and process CSV
        df = pd.read_csv(CSV_PATH)
        
        # Normalize column names
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
        
        course_id_int = int(course_id)
        course_data = df[df['course_id'] == course_id_int]
        
        if course_data.empty:
            flash(f'No data found for Course ID: {course_id}', 'warning')
            return redirect(url_for('namerform'))
        
        # Calculate statistics
        average = round(course_data['marks'].mean(), 2)
        maximum = course_data['marks'].max()
        
        # Generate histogram
        plt.figure(figsize=(8, 6))
        plt.hist(course_data['marks'], bins=10, color='skyblue', edgecolor='black')
        plt.title(f'Marks Distribution - Course {course_id}')
        plt.xlabel('Marks')
        plt.ylabel('Number of Students')
        plt.grid(axis='y', alpha=0.75)

        # Create directory for plots
        plot_dir = os.path.join('static', 'plots')
        
        # Simple directory creation - will not throw error if exists
        os.makedirs(plot_dir, exist_ok=True)
        
        # Save plot
        plot_filename = f'course_{course_id}_histogram.png'
        plot_path = os.path.join(plot_dir, plot_filename)
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        
        # Prepare plot URL
        plot_url = url_for('static', filename=f'plots/{plot_filename}')

        return render_template('courseid.html', 
                              average=average, 
                              maximum=maximum, 
                              course_id=course_id,
                              plot_url=plot_url)
    except Exception as e:
        flash(f'Error processing course data: {str(e)}', 'danger')
        return redirect(url_for('namerform'))
    
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template("index.html")

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

