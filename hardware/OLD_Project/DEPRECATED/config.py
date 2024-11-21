import os
from dotenv import load_dotenv
load_dotenv()

bind = f"{os.getenv('HOST')}:{os.getenv('PORT')}"
workers = os.getenv('WORKER')
timeout=300