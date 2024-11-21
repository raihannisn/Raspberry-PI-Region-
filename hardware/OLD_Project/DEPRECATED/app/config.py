import os

# Configuration settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'biofarma')
SQLALCHEMY_DATABASE_URI = 'sqlite:///biofarma.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
