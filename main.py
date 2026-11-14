import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect #CSRF protection for forms that change application data
from db import get_db_connection

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"] # Require a secret key from the environment
csrf = CSRFProtect(app) #Enable CSRF protection 


@app.get("/")
def home():
    return "Anime Library is running!"

@app.get("/register")
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=False)