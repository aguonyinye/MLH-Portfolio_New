import os
import csv
from werkzeug.utils import redirect
from flask import Flask, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# from . import db
# from app.db import get_db

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}".format(
    user=os.getenv("POSTGRES_USER"),
    passwd=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=5432,
    table=os.getenv("POSTGRES_DB"),
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UserModel(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."
        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    # TODO: Return a restister page
    return render_template("register.html", title="register")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            return "Login Successful", 200
        else:
            return error, 418

    # TODO: Return a login page
    return render_template("login.html", title="login")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    yechi = UserModel.query.filter_by(username="yechi").first()
    has_yechi = "yes" if yechi is not None else "no"
    return f"Works,has_yechi: {has_yechi}"
    


"""
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/works.html')
def works():
    return render_template('works.html')

@app.route('/work.html')
def work():
    return render_template('work.html')
"""


@app.route("/contactform", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        try:
            data = request.form.to_dict()
            form_data(data)
            message_form = (
                "Thank you for contacting me. I will get in touch with you shortly."
            )
            return render_template("submission.html", message=message_form)
        except request.DoesNotExist:
            message_form = "Database writing error!"
            return render_template("submission.html", message=message_form)
    else:
        message_form = "Form not submitted. Try again!"
        return render_template("submission.html", message=message_form)


@app.route("/<string:page_name>")
def page_direct(page_name="/"):
    try:
        return render_template(page_name)
    except request.DoesNotExist:
        return redirect("/")


def form_data(data):
    email = data["email"]
    subject = data["subject"]
    message = data["message"]
    with open("database.csv", "w", newline="") as csvfile:
        form_writer = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        form_writer.writerow([email, subject, message])
