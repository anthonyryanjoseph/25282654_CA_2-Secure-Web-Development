import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect #CSRF protection for forms that change application data
from db import get_db_connection
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from validators import validate_username, validate_password
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, render_template, request, session, redirect, url_for
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"] # Require a secret key from the environment
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax" #Makes session cookies harder to steal or misuse.
csrf = CSRFProtect(app) #Enable CSRF protection 
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://") #limits the amount of req a user could make.


@app.route("/")
def home():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        user = connection.execute("SELECT is_active FROM users WHERE id = ?",(user_id,)).fetchone()

    finally:
        connection.close()

    if user is None or user[0] != 1:  #Reject deleted or disabled accounts.
        session.clear()
        return redirect(url_for("login")) 

    connection = get_db_connection()

    try:
        collections = connection.execute(
        "SELECT id, name, is_public FROM collections WHERE owner_id = ? ORDER BY id DESC",(user_id,)).fetchall()
    finally:
       connection.close()

    return render_template("home.html", collections=collections)

@app.route("/collections/new", methods=["GET", "POST"])
def new_collection():
    user_id = session.get("user_id")

    if user_id is None:
      return redirect(url_for("login"))

    connection = get_db_connection()

    try:
         user = connection.execute(
          "SELECT is_active FROM users WHERE id = ?",(user_id,)).fetchone()
    finally:
         connection.close()
        
    if user is None or user[0] != 1:  # Stop disabled or deleted users from creating collections.
         session.clear()
         return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if not 1 <= len(name) <= 100:
          return "Collection name must be between 1 and 100 characters.", 400 #giving a check for the collection name in the server.
        
        connection = get_db_connection()

        try:
           connection.execute(
             "INSERT INTO collections (owner_id, name, is_public) VALUES (?, ?, ?)",(user_id, name, 0)) #parameterized
           connection.commit()
        finally:
           connection.close()

        return redirect(url_for("home"))
    return render_template("create_collection.html")

@app.get("/collections/<int:collection_id>")
def view_collection(collection_id):
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        user = connection.execute(
            "SELECT is_active FROM users WHERE id = ?",(user_id,)).fetchone()

        collection = None

        if user is not None and user[0] == 1:
            collection = connection.execute(
                "SELECT name FROM collections WHERE id = ? AND owner_id = ?",(collection_id, user_id)).fetchone() # Only allow users to open their own collections
    finally:
        connection.close()

    if user is None or user[0] != 1:
        session.clear()
        return redirect(url_for("login"))

    if collection is None:
        return "Collection not found.", 404

    return render_template("collection.html", collection_name=collection[0])

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"]) #limits
def register():
    if request.method == "POST" : 
        print("Registration Form submitted.")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        username_valid, username_error = validate_username(username)
        password_valid, password_error = validate_password(password)

        if not username_valid:
            return render_template("register.html", error=username_error), 400 #check if username valid

        if not password_valid:
            return render_template("register.html", error=password_error), 400 #check if password valid
    
        if password != confirm_password:
            return render_template( "register.html", error="Passwords do not match."), 400 #check if both passwrod match

        password_hash = generate_password_hash(password) #hashin the password

        insert_sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"

        connection = get_db_connection()

        try:
            connection.execute(insert_sql, (username, password_hash))
            connection.commit()

        except sqlite3.IntegrityError as error:
              if error.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                 return render_template("register.html", error="Username is already taken."), 409 # Show a message if the username is already taken.
              raise
        
        finally:
            connection.close()
        return render_template("register.html",success="Account created successfully!"), 201

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"]) #to avoid bruteforcing
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db_connection()

        try:
            user = connection.execute("SELECT id, username, password_hash," \
            " role, is_active FROM users WHERE username = ? COLLATE NOCASE",(username,)).fetchone()

        finally:
           connection.close()

        if user is None:
           return render_template("login.html", error="Invalid username or password."), 401 #check if the user exists.
        
        if not check_password_hash(user[2], password):
           return render_template("login.html", error="Invalid username or password."), 401 #check if the password matches the hash

        if user[4] != 1:
           return render_template("login.html", error="Invalid username or password."), 401 #stops disabled accounts from logging in.
        session.clear()
        session["user_id"] = user[0] 
        return redirect(url_for("home"))

    return render_template("login.html")

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=False)