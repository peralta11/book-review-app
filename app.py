import os
import requests
from flask import Flask, session, render_template, request, flash, redirect, url_for, logging,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import psycopg2


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))




@app.route("/")
def index():
    ls = db.execute('select username, email from users').fetchall()
    print(ls)
    return "Project 1 "

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='password donot match')
    ])
    confirm = PasswordField('Confirm Password')
@app.route('/register', methods=['GET','POST'])
def register():
    db.execute('CREATE TABLE IF NOT EXISTS users (name VARCHAR , email VARCHAR, username VARCHAR, password VARCHAR)')
    db.commit()
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        
        check = db.execute('select username, email from users').fetchall()
        #print(type(check))--- list
        for i in check:
            if (username,email) == (i[0],i[1]):
                flash('username or email already exists')
                return redirect(url_for('register'))
            else:
                db.execute("insert into users(name, email, username, password) values(:name, :email, :username, :password)",{"name":name, "email":email, "username":username, "password":password})
                db.commit()
                flash('registered','success')
        
    return render_template('register.html', form=form) 
# user_login

@app.route('/login', methods=["GET","POST"])
def login():

    
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        result = db.execute("select * from users where (username=:username)",{"username":username}).fetchone()
        try:
            #get stored hash
            password = result['password']

            #comapare password

            if sha256_crypt.verify(password_candidate,password):
                #passed
                session['logged_in'] = True
                session['username'] = username
                flash('you are now logged in','success')
                return redirect(url_for('dashboard'))

            else:
                error = 'invalid login'
                return render_template("login.html",error=error)
            db.close()
        except:
            error = "username not found"
            return render_template('login.html',error=error)
        

    return render_template('login.html')  
#check authorization
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('unauthorized access, please login')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
#@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=["GET","POST"])
#@is_logged_in
def dashboard():

    task_title = request.form.get('task_title')
    task_author = request.form.get('task_author')
    task_year = request.form.get('task_year')
    task_isbn = request.form.get('task_isbn')

    
    result_books = db.execute('SELECT * FROM books WHERE (isbn=:isbn) OR (author=:author) OR (title=:title) OR (year=:year)',{"isbn":task_isbn, "author":task_author, "title":task_title, "year":task_year}).fetchall()
    print(result_books)

    return render_template('dashboard.html',result_books = result_books)


class reviewform(Form):
    review = TextAreaField('review', [validators.length(min=10)])


@app.route('/booksreview/<isbn>', methods=["GET","POST"])
#@is_logged_in
def booksreview(isbn):
    
    db.execute('CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, isbn VARCHAR, userid VARCHAR, bookreview VARCHAR)')
    db.commit()
    all_reviews = db.execute('select * from books, reviews where books.isbn = reviews.isbn')
    rv = db.execute('select author, title from books where (isbn=:isbn)',{"isbn":isbn})


    form = reviewform(request.form)
    if request.method == 'POST' and form.validate():
        review = form.review.data
        #execute
        db.execute('INSERT INTO reviews(isbn, bookreview, userid) VALUES(:isbn,:bookreview, :session)', {"isbn":isbn, "bookreview":review, "session":session['username']})
        db.commit()
        return redirect(url_for('booksreview',isbn=isbn))

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "COuZEDwalN3ZVOz3uPCCWw", "isbns": isbn})
    rv = res.json()['books']
    #rv is a list of dictionary
    #extracting the dictionary from list
    data = rv[0]
    new_data = data['average_rating']
    
    return render_template('booksreview.html', form=form, all_reviews = all_reviews, isbn=isbn, new_data=new_data)




if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)