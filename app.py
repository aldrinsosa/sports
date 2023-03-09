from flask import Flask, request, session, render_template, redirect
from flask_session import Session
from cs50 import SQL

# Initialize app,session and database
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///registrants.db")

SPORTS = [
    "Basketball",
    "Football",
    "Volley",
    "Tenis"
]


@app.route('/')
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html", sports=SPORTS, name=session["name"])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session["name"] = request.form.get("name")
        return redirect('/')
    return render_template("login.html")


@app.route('/register', methods=['POST'])
def register():
    # Getting the name and the sport
    name = session["name"]
    sport = request.form.get("sports")

    # Checking the input
    if not name or sport not in SPORTS:
        return render_template("failure.html", code="not")

    # Check if are already registered in that sport
    person_sports = db.execute(
        "SELECT Sport FROM registrants WHERE name = ?", name)
    for sports in person_sports:
        if sport == sports["Sport"]:
            return render_template("failure.html", code="already")

    # Putting the data in the db
    db.execute(
        "INSERT INTO registrants (Name, Sport) VALUES (?, ?)", name, sport)
    return redirect("/registrants")


@app.route('/registrants')
def registrants():
    if not session.get("name"):
        return redirect("/login")
    # Render the registered sports
    return render_template("registrants.html", registrants=db.execute("SELECT * FROM registrants WHERE Name in (?)", session["name"]))


@app.route('/deregister', methods=['POST', 'GET'])
def deregister():
    # Delete the register in the db
    if request.method == "POST":
        db.execute("DELETE FROM registrants WHERE Id = ?",
                   request.form.get("id"))
        return redirect("/registrants")
    return redirect("/")


@app.route('/logout')
def logout():
    session["name"] = None
    return redirect("/")
