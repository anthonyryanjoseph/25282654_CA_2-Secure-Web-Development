Anime Library System

Project Overview 
-The project is about an Anime Library system is a web application that is used for managing anime records. Currently I plan on using Flask and SQlite for the backend with separate permissions for Users and Admins. 

The project will focus more on the security aspect rather than graphics, it will include password hashes, parameterized databases and CSFR protection with secure session handling. These protections will be tested and also documented throughout the SDLC. 

Technologies 
-Python & Flask 

Planned Security features
-Password hashing, permissions, parameterized SQL, CSFR protection, login throttling 

##Installation and Setup 
create a virtual environment: 
python -m venv .venv

Activate it: 
.\.venv\Scripts\Activate.ps1

Install the Libraries : 
python -m pip install Flask
python -m pip install Flask-WTF
python -m pip install python-dotenv
python -m pip install Flask-Limiter

Confirgure a secret key: 
python -c "import secrets; print(secrets.token_hex(32))"

Put the secret key in the .env file : 
FLASK_SECRET_KEY=PASTE_GENERATED_KEY_HERE (-paste the hex value generated)

Initialize the sqlite databse 
python -c "from db import init_db; init_db()"


Start the app:
python main.py



