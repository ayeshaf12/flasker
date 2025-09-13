from flask import Flask, render_template, flash, redirect, url_for, send_from_directory, request
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField
from wtforms.validators import DataRequired
import csv
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime, timezone
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# MySQL connection function
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Ummeayesha@123',
            database='our_users',
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Create a form class 
class UserForm(FlaskForm):
    name = StringField(" Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Initialize database
def init_db():
    connection = None
    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS our_users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        email VARCHAR(200) NOT NULL UNIQUE,
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                connection.commit()
                print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection:
            connection.close()

# Create a name page
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    our_users = []
    
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        
        connection = None
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    # Check if email already exists
                    cursor.execute("SELECT * FROM our_users WHERE email = %s", (email,))
                    existing_user = cursor.fetchone()
                    
                    if existing_user is None:
                        # Add new user
                        cursor.execute("INSERT INTO our_users (name, email) VALUES (%s, %s)", (name, email))
                        connection.commit()
                        
                        flash(f"Hello {name}! Your account has been created successfully.", "success")
                        form.name.data = ''
                        form.email.data = ''
                        
                        return redirect(url_for('success'))
                    else:
                        flash("A user with that email already exists.", "error")
        except Exception as e:
            flash(f"Error adding user: {str(e)}", "danger")
        finally:
            if connection:
                connection.close()
    
    # Get all users
    connection = None
    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM our_users ORDER BY date_added")
                our_users = cursor.fetchall()
    except Exception as e:
        flash(f"Error retrieving users: {str(e)}", "danger")
    finally:
        if connection:
            connection.close()
    
    return render_template("add_user1.html", form=form, our_users=our_users, name=name)

# Success page route
@app.route('/success')
def success():
    return render_template("success.html")

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
        
        if id_type == 'student':
            return redirect(url_for('student_details', student_id=id_value))
        elif id_type == 'course':
            return redirect(url_for('course_statistics', course_id=id_value))
    
    return render_template("namerform.html", form=form)

CSV_PATH = 'data.csv'

def load_and_clean_data():
    df = pd.read_csv(CSV_PATH)
    df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
    return df

@app.route('/student/<student_id>')
def student_details(student_id):
    try:
        df = load_and_clean_data()  
        student_id_int = int(student_id)
        student_data = df[df['student_id'] == student_id_int]
        
        if student_data.empty:
            flash(f'No data found for Student ID: {student_id}', 'warning')
            return redirect(url_for('namerform'))
        
        total_marks = student_data['marks'].sum()
        records = student_data.to_dict('records')
        flash("Congratulations on your graduation !!!")

        return render_template('studentid.html', records=records, total_marks=total_marks, student_id=student_id)
    except Exception as e:
        flash(f'Error processing student data: {str(e)}', 'danger')
        return redirect(url_for('namerform'))

@app.route('/course/<course_id>')
def course_statistics(course_id):
    try:
        df = load_and_clean_data()
        course_id_int = int(course_id)
        course_data = df[df['course_id'] == course_id_int]
        if course_data.empty:
            flash(f'Your Course ID doesnt exist contact your DSO : {course_id}', 'warning')
            return redirect(url_for('namerform'))
        
        average = round(course_data['marks'].mean(), 2)
        maximum = course_data['marks'].max()
    
        plt.figure(figsize=(8, 6))
        plt.hist(course_data['marks'], bins=10, color='skyblue', edgecolor='black')
        plt.title(f'Marks Distribution - Course {course_id}')
        plt.xlabel('Marks')
        plt.ylabel('Number of Students')
        plt.grid(axis='y', alpha=0.75)
        
        plot_dir = os.path.join('static', 'plots')
        os.makedirs(plot_dir, exist_ok=True)
        
        plot_filename = f'course_{course_id}_histogram.png'
        plot_path = os.path.join(plot_dir, plot_filename)
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        
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

@app.route('/user/<name>')
def user(name):
    return "<h1>Hello {}</h1>".format(name)

@app.route('/add/')
def add():
    first_name= "Jessica"
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)