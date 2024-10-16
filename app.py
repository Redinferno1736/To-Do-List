import os
import requests
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from pymongo import MongoClient

app = Flask(__name__)
application = app

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

MONGODB_URI = "mongodb+srv://todolist:todolist@todolist.0ozmp.mongodb.net/?retryWrites=true&w=majority&appName=ToDoList"

client = MongoClient(MONGODB_URI)
db = client.todo 
users_collection = db.users

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message):
    return render_template("apology.html", message=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            return apology("Please make sure the passwords match")

        hash = generate_password_hash(password)

        user = {"username": username, "hash": hash}
        users_collection.insert_one(user)

        return redirect('/')
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        user = users_collection.find_one({"username": request.form.get("username")})

        if user is None or not check_password_hash(user["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = str(user["_id"])

        return redirect("/")

    else:
        return render_template("login.html")
    
@app.route("/")
@login_req
def index():
    user_id = session["user_id"]