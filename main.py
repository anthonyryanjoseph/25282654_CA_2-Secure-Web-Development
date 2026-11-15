import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect #CSRF protection for forms that change application data
from db import get_db_connection
from werkzeug.security import generate_password_hash
from validators import validate_username, validate_password

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"] # Require a secret key from the environment
csrf = CSRFProtect(app) #Enable CSRF protection 


@app.get("/")
def home():
    return "Anime Library is running!"

@app.route("/register", methods=["GET", "POST"])
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


if __name__ == "__main__":
    app.run(debug=False)