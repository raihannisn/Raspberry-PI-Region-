1. pip install -r requirements.txt
2. flask db init
3. flask db upgrade
4. flask crontab add
5. env.example to .env
6. gunicorn -k eventlet -c config.py app:app --reload

# Raspberry
1. cd raspberry
2. flask run -e motor:app --port=6000 --reload