import os

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


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


@app.route("/", methods=["POST", "GET"])
def index():
    loggedin = False
    if request.method == "GET":
        pass

    return render_template("index.html", loggedin=loggedin)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/evaluate")
def evaluate():
    username = request.form.get("username")
    password = request.form.get("password")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/thanks", methods=["post"])
def thanks():

    name = request.form.get("name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": "Suban"}).rowcount > 0:
        return redirect(url_for('signup'))

    print(f"name: {name}, username: {username}, email: {email},password:{password}")
    db.execute("INSERT INTO users (name, username, email, password) VALUES (:name, :username, :email, :password)", {
        "name": name, "username": username, "email": email, "password": password
        })

    db.commit()


    return "<h1>Thanks For Registering</h1>"
