import os
import requests
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from pymongo import MongoClient
from datetime import date

app = Flask(__name__)
application = app

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)
Session(app)

MONGODB_URI = "mongodb://localhost:27017"

client = MongoClient(MONGODB_URI)
db = client.Todo 
users_collection = db.users
tasks_collection = db.tasks

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
        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one({"username": username})

        if user is None:
            return apology("invalid username")
        if not check_password_hash(user["hash"], password):
            return apology("invalid password")

        session["user_id"] = str(user["_id"])

        return redirect("/")

    return render_template("login.html")

@app.route("/add", methods=["GET", "POST"])
@login_req
def add():
    user_id = session["user_id"]
    if request.method == "POST":
        task=request.form.get("task")
        date=date.today()
        task={"user_id": user_id, "task": task, "date": date}
        tasks_collection.insert_one(task)
        return redirect("/")
    else:
        return render_template("add.html")

@app.route("/")
@login_req
def index():
    user_id = session["user_id"]
    tasks=db.tasks.find({"user_id": user_id})
    len_dates = {}
    t = {}
    for row in tasks:
        task = row["task"]
        date = row["date"]
        if date not in len_dates:
            len_dates[date] = 1
        else:
            len_dates[date] += 1
        if date not in t:
            t[date] = [task]
        else:
            t[date].append([task])
    return render_template("index.html", t=t, len_dates=len_dates)

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
