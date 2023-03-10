from flask import Flask, request, session, render_template, redirect, flash
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import InputRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, check_password_hash

# Initialize app
app = Flask(__name__, instance_relative_config=True)

# Config
app.config.from_pyfile('config.py')

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Encryption
bcrypt = Bcrypt(app)

# DB initialization
db = SQLAlchemy(app)

# Create Tables


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Sports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport = db.Column(db.String(20), nullable=False)
    usernameId = db.Column(db.Integer, db.ForeignKey('users.id'))


class Register(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Name", "autofocus": "True", "autocomplete": "off"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=8, max=20)], render_kw={"placeholder": "Password", "autocomplete": "off"})
    submit = SubmitField("Register")


class Login(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Name", "autofocus": "True", "autocomplete": "off"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=8, max=20)], render_kw={"placeholder": "Password", "autocomplete": "off"})

    submit = SubmitField("Login")


SPORTS = [
    "Basketball",
    "Football",
    "Volley",
    "Tenis"
]


@app.route('/')
@login_required
def index():
    # todo
    return render_template("index.html", sports=SPORTS, name=current_user.username)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # get the form from the class
    form = Register()

    if form.validate_on_submit():
        # crypt the password
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            flash("This user is already used")
            return redirect("/signup")

        crypted_pass = bcrypt.generate_password_hash(form.password.data)

        # add new user to the db
        db.session.add(Users(username=form.username.data,
                             password=crypted_pass))
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect("/")
            flash("Incorrect password")
            return redirect("/login")
        flash("Incorrect username")
        return redirect("/login")
    return render_template("login.html", form=form)


@app.route('/register', methods=['POST'])
@login_required
def register():
    # Getting sport
    sport = request.form.get("sports")

    # Checking the input
    if sport not in SPORTS:
        flash("Select a sport")
        return redirect("/")

    # Check if are already registered in that sport
    person_sports = Sports.query.filter_by(
        sport=sport, usernameId=current_user.id).first()
    if person_sports:
        flash("You're already in that sport")
        return redirect("/")

    # Putting the data in the db
    db.session.add(Sports(usernameId=current_user.id, sport=sport))
    db.session.commit()
    return redirect("/sports")


@app.route('/sports')
@login_required
def sports():
    # Render the registered sports
    sports = Sports.query.filter(Sports.usernameId == current_user.id).all()
    print(sports)
    return render_template("sports.html", registrants=Sports.query.filter(Sports.usernameId == current_user.id).all())


@app.route('/deregister', methods=['POST', 'GET'])
def deregister():
    # Delete the register in the db
    if request.method == "POST":
        sport = Sports.query.filter_by(id=request.form.get("id")).first()
        db.session.delete(sport)
        db.session.commit()
        return redirect("/sports")
    return redirect("/")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")
