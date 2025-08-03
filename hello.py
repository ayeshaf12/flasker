from flask import Flask,render_template


app= Flask(__name__)

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
    


# @app.route('/users/<name>')
# def users(name):
#     return render_template("user.html",user_name=name)


@app.errorhandler(404)
def error_page(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def error_page(e):
    return render_template("500.html"), 500

if __name__=='__main__':
    app.run(debug=True)

