import os, json, ast, requests

from flask import Flask, session, render_template, request, redirect, jsonify, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt
from models import *

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.secret_key = "cs50-project1"

#init database
db.init_app(app)

#init session
Session(app)

#init bcrypt for encrypted passwords
bcrypt = Bcrypt(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        #if the request isn't contain username, return error message.
        if not request.form.get("username"):
            return render_template("errors.html", message = "Please insert username")

        #if the request isn't contain email, return error message.
        elif not request.form.get("email"):
            return render_template("errors.html", message = "Please, insert email")

        #if the request isn't contain password, return error message.
        elif not request.form.get("password"):
            return render_template("errors.html", message = "Please, insert new password")

        #if the request isn't contain confirmation password, return error message.
        elif not request.form.get("confirmation"):
            return render_template("errors.html", message = "Please, insert repeat password")

        #if the request password isn't egal to confirmation password, return error message.
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("errors.html", message = "Yours passwords don't match")

        else:
            #variable that take data in request password and encrypt with bcrypt
            hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8")

            #variable that take from post request username, email and encrypted password in a table fonction
            adduser = Users(username = request.form.get("username"), email = request.form.get("email"), password = hashed_password)

            #post request username
            username = request.form.get("username")

            #post request email
            email = request.form.get("email")

            #username query
            userslist = db.execute("SELECT username FROM users WHERE username=(:username)",
                        {"username":username}).fetchone()

            #email query
            emailslist = db.execute("SELECT email FROM users WHERE email=(:email)",
                        {"email":email}).fetchone()

            #check if username already exist
            if userslist != None:
                return render_template("errors.html", message = "User already exist")

            #check if email already exist
            elif emailslist != None:
                return render_template("errors.html", message = "Email already exist")
            else:
                #add user in table
                db.add(adduser)
                db.commit()
                return redirect(url_for('success'))

    else:
        return render_template("register.html")


@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/errors")
def errors():
    return render_template("errors.html")

@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        #username request
        username = request.form.get("loginUsername")

        #password request
        password = request.form.get("loginPassword")

        #username query that return row
        check = db.execute("SELECT * FROM users WHERE username = :username",
                    {"username":username}).fetchone()

        print(check)

        #user id of the username query in session
        session["user_id"] = check[0]

        #username of the username query in session
        session["user"] = check[1]

        #if not request username return error
        if not username:
            return render_template("errors.html", message = "Please insert username")

        #if not request password return error
        elif not password:
            return render_template("errors.html", message = "Please insert password")

        #check username
        elif check[1] == None:
            return render_template("errors.html", message = "User don't exist. Please register")

        #check password
        elif not bcrypt.check_password_hash(check[3], password):
            return render_template("errors.html", message = "Wrong password")

        #if logged, redirect to search
        elif "user" in session:
            return redirect(url_for("search", user = username))

    else:
        return render_template("login.html")


@app.route("/logout", methods=["POST", "GET"])
def logout():

    # erase session
    session.clear()

    return render_template("index.html")

# search page
@app.route("/<user>/search", methods=["POST", "GET"])
def search(user):

    #variable that contain username
    username = session["user"]

    if request.method == "POST":

        # search request
        if request.form.get("search"):

            # variable search request
            getsearch = request.form.get("search")

            # add wildcard to match multi words
            getsearch = '%' + getsearch + '%'

            # add a capital letter at the beginning of query
            getsearch = getsearch.title()

            # query to search book infos in books table
            query = db.execute("SELECT isbn, title, author, year FROM books WHERE (isbn LIKE :getsearch) OR (title LIKE :getsearch) OR (author LIKE :getsearch) OR (year LIKE :getsearch)",
            {"getsearch": getsearch}).fetchall()

            # if query don't get result
            if len(query) == 0:
                return render_template("errors.html", message = "No result")

            else:
                # erase session.query in session if it exist
                session.pop("query", None)

                # create session.query
                session["query"] = query

                return redirect(url_for("result", user = username))

        else:
            return render_template("{{user}}/search.html", user = username)

    else:
        return render_template("{{user}}/search.html", user = username)

# results page
@app.route("/<user>/result", methods=["POST", "GET"])
def result(user):
    result = session["query"]

    # variable username from session
    username = session["user"]

    return render_template("{{user}}/result.html", user = username, result = result, length = len(result))

# book page
@app.route("/<user>/<book>", methods=["POST", "GET"])
def book(user, book):

    if request.method == 'POST':

        # request to book table
        query = db.execute("SELECT isbn, title, author, year FROM books WHERE (title LIKE :book)",
        {"book": book}).fetchone()

        # put session.user into a variable
        rev_username = session["user"]

        # put query.isbn into a variable
        rev_isbn = query[0]

        # use rewiews class with some values and put into a variable
        addreview = Reviews(rev_isbn = rev_isbn, rev_username = rev_username, review = request.form.get("review"), rate = request.form.get("rate"))

        # request isbn from review for the username and put into a variable
        check = db.execute("SELECT rev_isbn FROM reviews WHERE rev_username=(:rev_username)",
                    {"rev_username":rev_username}).fetchone()

        if not request.form.get("review"):
            return render_template('/errors.html', message = "Please, insert a review.")

        if not request.form.get("rate"):
            return render_template('/errors.html', message = "Please, rate the book.")

        elif check != None:
            return render_template('/errors.html', message = "You already had posted a review for this book")

        else:
            # add a review into review table
            db.add(addreview)
            db.commit()
            return render_template('/success.html', message = "You review is submitted!")

    if request.method == 'GET':

        # request to book table
        query = db.execute("SELECT isbn, title, author, year FROM books WHERE (title LIKE :book)",
        {"book": book}).fetchone()

        # goodreads api request into a variable
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "rPpQMNygX27uKlbVg3SzQ", "isbns": query[0]}).json()

        # res.books
        res = res["books"]

        res = res[0]

        rev_username = session["user"]

        rev_isbn = query[0]

        # request from review with isbn
        all_reviews = db.execute("SELECT rev_username, review, rate FROM reviews WHERE rev_isbn=(:rev_isbn)",
                    {"rev_isbn":rev_isbn}).fetchall()

        lenght = len(all_reviews)
        return render_template("{{user}}/{{book}}.html", user = user, book = book, query = query, res = res, lenght = lenght, all_reviews = all_reviews)

# api response to GET requests
@app.route("/api/<isbn>", methods=["POST", "GET"])
def get_api(isbn):
    if request.method == 'GET':

        # isbn integer to string
        str_isbn = str(isbn)

        # request from books infos needed into a variable
        query = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn=(:str_isbn)",
        {"str_isbn" :str_isbn}).fetchone()

        # turn query into a dictionnary
        d = dict(query.items())

        # list of all values
        a = list(d.values())

        if not len(a) == 0:
            query_isbn = a[0]
            query_title = a[1]
            query_author = a[2]
            query_year = a[3]
            query_year = int(query_year)
            all_reviews = db.execute("SELECT review, rate FROM reviews WHERE rev_isbn=(:query_isbn)",
                        {"query_isbn":query_isbn}).fetchall()

            # turn all_reviews into a dictionnary
            k = dict(all_reviews)

            # turn all k values into a list
            l = list(k.values())

            # turn all string to integer in a list
            l = list(map(int, l))

            # sum of a list
            m = sum(l)

            if not m == 0:
                rate_sum = float(m)
                review_float = len(l)
                review_float = float(review_float)
                average_score = rate_sum / review_float
                review_count = int(review_float)

                json_query = {
                    "title": query_title,
                    "author": query_author,
                    "year": query_year,
                    "isbn": str_isbn,
                    "review_count": review_count,
                    "average_score": average_score
                }

                return jsonify(json_query)

            else:
                return render_template('errors.html', message = "404 error"), 404

        else:
            return render_template('errors.html', message = "404 error"), 404

    else:
        return render_template('errors.html', message = "404 error"), 404
