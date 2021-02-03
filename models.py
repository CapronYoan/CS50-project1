from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)

    def __init__(self, isbn, title, author, year):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    rev_isbn = db.Column(db.String, nullable=False)
    rev_username = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    rate = db.Column(db.String, nullable=False)

    def __init__(self, rev_isbn, rev_username, review, rate):
        self.rev_isbn = rev_isbn
        self.rev_username = rev_username
        self.review = review
        self.rate = rate
