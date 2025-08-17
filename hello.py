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
    if form.validate_on_submit():   #checks if form is submitted and validated means data was passed for each field
        id_type = form.id_type.data
        id_value = form.id_value.data
        
        # Match the values to your choices
        if id_type == 'student':
            return redirect(url_for('student_details', student_id=id_value))
        elif id_type == 'course':
            return redirect(url_for('course_statistics', course_id=id_value))
    
    return render_template("namerform.html", form=form)


CSV_PATH = 'data.csv'  # Make sure this is in the same directory

@app.route('/student/<student_id>')             #student_id is a variable here
def student_details(student_id):                #student_id is an argument here 
    try:
    # Read CSV with proper column names
        df = pd.read_csv(CSV_PATH)
     #a string method that removes whitespaces from each string in the column index only leading/trailing spaces.    
        df.columns = df.columns.str.strip() 
   
     # Convert to integer for comparison.student_id_int is a new variable here
        student_id_int = int(student_id)
    # This filters the DataFrame `df` to only include rows where the column 'Student id' (with spaces) matches the integer `student_id_int`.The result is a new DataFrame (subset of the original) stored in `student_data`.
    #df['Student id']→ Look at the "Student id" column in your class list
    # == student_id_int→ Find all entries that exactly match the ID number you're searching for
    # df[ ... ] → Filter the entire class list to keep only the rows where the ID matches
        student_data = df[df['Student id'] == student_id_int] 
    #  Key point: This handles the "not found" case gracefully by informing the user and returning them to the form to try again.
        if student_data.empty:
            flash(f'No data found for Student ID: {student_id}', 'warning')
            return redirect(url_for('namerform'))
        
    # Calculate total marks
        total_marks = student_data['Marks'].sum()
        
    # Flask uses Jinja2 templates. Jinja2 can easily loop over a list of dictionaries but cannot directly handle a pandas DataFrame. The dictionary format is more natural for templating.
        records = student_data.to_dict('records') 
        
        return render_template('studentid.html',records=records,total_marks=total_marks,student_id=student_id)
    # Without this, if an error occurs (e.g., file not found, data corruption, unexpected type Flask would return a 500 Internal Server Error page, which is not user-friendly.
    except Exception as e:
        flash(f'Error processing student data: {str(e)}', 'danger')
        return redirect(url_for('namerform'))


@app.route('/course/<course_id>')
def course_statistics(course_id):
    try:
    # Read and process CSV
        df = pd.read_csv(CSV_PATH)
        
    # After Transformation:['student_id', 'first_name', 'exam_date', 'total_marks']
    ### Best Approach:**Clean the DataFrame once when it's loaded (or reloaded) and then use the cleaned version everywhere.**
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
        
        course_id_int = int(course_id)
    # Find all entries that exactly match the ID number you're searching for and only keep the ID selected. 
        course_data = df[df['course_id'] == course_id_int]
        
        if course_data.empty:
            flash(f'No data found for Course ID: {course_id}', 'warning')
            return redirect(url_for('namerform'))
        
# Calculate statistics
        average = round(course_data['marks'].mean(), 2)
        maximum = course_data['marks'].max()
        
# Generate histogram
        plt.figure(figsize=(8, 6)) #A blank rectangle 8 inches wide × 6 inches tall
        plt.hist(course_data['marks'], bins=10, color='skyblue', edgecolor='black') #Skyblue bars with black borders showing how many students got each mark range .Marks (Bins)

# Add Labels and Title
        plt.title(f'Marks Distribution - Course {course_id}')
        plt.xlabel('Marks')
        plt.ylabel('Number of Students')
        plt.grid(axis='y', alpha=0.75) #grid lines only for Y-axis
        # plt.grid(axis='x', alpha=0.25)

# Create directory for plots
# - You decide to save this drawing in a folder named 'plots' inside the 'static' folder of your project.
        plot_dir = os.path.join('static', 'plots')
#Creates folder: your-project/static/plots/
# Simple directory creation - will not throw error if exists
# - `os.makedirs` creates the folder if it doesn't exist. If it already exists, it doesn't complain (`exist_ok=True`).
        os.makedirs(plot_dir, exist_ok=True)
        
# Save plot-Name plot
        plot_filename = f'course_{course_id}_histogram.png'  #Name of the image
        plot_path = os.path.join(plot_dir, plot_filename)
        plt.savefig(plot_path, bbox_inches='tight')  #`bbox_inches='tight'` means you trim any extra white space around the drawing.
        plt.close()
        
    # Prepare plot URL -http://127.0.0.1:5000/course/2002
    #URL -`/static/plots/course_2001_histogram.png`
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



################################
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

