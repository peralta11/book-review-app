import os

from flask import Flask, session, render_template, request, flash, redirect, url_for, logging
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

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
        

        db.execute("insert into users(name, email, username, password) values(:name, :email, :username, :password)",{"name":name, "email":email, "username":username, "password":password})
        db.commit()
        flash('registered','success')
        redirect(url_for('index'))
    return render_template('register.html', form=form) 
    


if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)