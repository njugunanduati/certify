# retaen
Certify Application 

# creating the virtual enviroment
python3 -m venv venv

# setting the dependancies
# 1) upgrade pip

pip install --upgrade pip

# 2) install the requirements
pip install -r requirements.txt


# Running the application

# 1) Setting up the FLASK_APP

export FLASK_APP=certify.py

# 2) Set up the database

# open the mysql and create a database
create database certify;

# run the migrateions
# 1) Initialize the migration
flask db init

# 2) upgrade the migration 
flask db upgrade

# 3) Migrate 
flask db migrate

# 4)Run the application
flask run

