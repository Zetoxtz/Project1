import os

from flask import Flask, session, render_template, request, url_for, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests


KEY = "qDinAD9D4vjRcTVkG6UEw"
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
    if request.method == "GET":
        pass
    if session.get("isLoggedIn", False):
        print(session.get('user', None).username)
    return render_template("index.html", isLoggedIn=session.get('isLoggedIn', False), user=session.get('user', None))


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("search")

    matches = []

    matches+=(db.execute("SELECT * FROM books WHERE lower(isbn) LIKE lower(:isbn)", {"isbn": "%" + query + "%"}).fetchall())
    matches+=(db.execute("SELECT * FROM books WHERE lower(title) LIKE lower(:title)", {'title': "%" + query + "%"}).fetchall())
    matches+=(db.execute("SELECT * FROM books WHERE lower(author) LIKE lower(:author)", {'author': "%" + query + "%"}).fetchall())
    print(matches)


    return render_template("search.html", matches=matches, query=query, user=session.get('user', None), isLoggedIn=session.get("isLoggedIn", False))


@app.route("/login")
def login():
    if session.get("isLoggedIn", False):
        return redirect(url_for('index'))
    return render_template("login.html", isLoggedIn=session.get("isLoggedIn", False), user=session.get('user', None))


@app.route("/evaluate", methods=["post"])
def evaluate():
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username=:username AND password=:password",
                  {"username": username, "password": password}).rowcount == 0:
        return "no user"

    session["user"] = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
                                 {"username": username, "password": password}).fetchone()
    session['isLoggedIn'] = True
    return redirect(url_for('index'))


@app.route("/signup")
def signup():
    if session.get("isLoggedIn", False):
        return redirect(url_for('index'))
    return render_template("signup.html", isLoggedIn=session.get("isLoggedIn", False), user=session.get('user', None))


@app.route("/logout")
def logout():
    session['isLoggedIn'] = False
    session['user'] = None

    return redirect(url_for('index'))


@app.route("/thanks", methods=["post"])
def thanks():
    name = request.form.get("name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
        return redirect(url_for('signup'))

    print(f"name: {name}, username: {username}, email: {email},password:{password}")
    db.execute("INSERT INTO users (name, username, email, password) VALUES (:name, :username, :email, :password)", {
        "name": name, "username": username, "email": email, "password": password
    })

    db.commit()

    return "<h1>Thanks For Registering</h1>"


@app.route("/books/<string:isbn>")
def books(isbn):
    book = (db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone())

    reviews = db.execute("SELECT * FROM reviews WHERE isbn= :isbn", {"isbn": isbn}).fetchall()

    has_review = False
    try:
        if db.execute("SELECT * FROM reviews WHERE username = :username", {"username": session['user'].username}).rowcount > 0:
            has_review = True
        else:
            has_review = False
    except:
        has_review = True

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    if res.status_code == 200:
        res = res.json()
        goodreads_work_ratings_count = res.get("books", None)[0].get("work_ratings_count", None)
        goodreads_average_rating = res.get("books", None)[0].get("average_rating", None)

    return render_template("books.html", isbn=isbn, book=book, isLoggedIn=session.get('isLoggedIn', False), user=session.get('user', None), reviews=reviews, has_review=has_review, goodreads_work_ratings_count=goodreads_work_ratings_count, goodreads_average_rating=goodreads_average_rating)


@app.route("/submit/<string:isbn>", methods=["post"])
def submit(isbn):
    review = request.form.get("review")
    star = request.form.get("star")

    if not session.get('isLoggedIn', False):
        return redirect(url_for('login'))

    username = session['user'].username

    db.execute("INSERT INTO reviews (username, isbn, review, star) VALUES (:username, :isbn, :review, :star)", {
        "username": username, "isbn": isbn, "review": review, "star": star
    })
    db.commit()

    return redirect(url_for('books', isbn=isbn))

@app.route("/api/<string:isbn>")
def api(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn=:isbn ", {"isbn": isbn}).fetchone()

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})

    if res.status_code == 200:
        goodreads_average_rating = res.json()['books'][0]['average_rating']
        goodreads_work_ratings_count = res.json()['books'][0]['work_ratings_count']
    else:
        goodreads_average_rating = 0
        goodreads_work_ratings_count = 0

    if book is None:
        return jsonify({"error": "Invalid Book isbn"}), 422
    return jsonify ({
        "author": book.author,
        "title": book.title,
        "year" : book.year,
        "isbn": book.isbn,
        "review_count": goodreads_work_ratings_count,
        "average_rating": goodreads_average_rating
    })
