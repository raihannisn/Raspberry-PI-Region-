from app import crontab, db
from app.models import Setting
from dotenv import load_dotenv
import requests
import os
import logging
load_dotenv()

@crontab.job("*")
def update_setting():
    item = Setting.query.first()
    if item:
        try:
            if item.is_uptodate == False:
                response = requests.get(f"{os.getenv('BACKEND_URL')}/api/auth/connection")
                if response.status_code == 200:
                    batch_id = os.getenv('BATCH_ID')
                    microscope_id = os.getenv('MICROSCOPE_ID')
                    auth = requests.post(f"{os.getenv('BACKEND_URL')}/api/auth/login", json={'username': 'superadmin', 'password': 'password'}).json().get('data').get('token')
                    headers = {'Authorization': f'Bearer {auth}'}
                    microscope_batch = requests.get(f"{os.getenv('BACKEND_URL')}/api/batch/setting/show/{batch_id}?microscope={microscope_id}", headers=headers).json()
                    if microscope_batch.get('status') == True:
                        batch_microscope_setting_id = microscope_batch.get('data').get('id')
                        requests.post(f"{os.getenv('BACKEND_URL')}/api/batch/setting/update/{batch_microscope_setting_id}/cloud",headers=headers, json=item.item_setting()).json()
                        setattr(item, 'is_uptodate', True)
                        db.session.commit()
        except Exception as e:
            logging.error(f'An error occurred: {str(e)}')

@crontab.job("*")
def upload_cpe():
    folder_path = 'storage/cpe'
    files = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            files.append(('images[]', (filename, open(file_path, 'rb'))))

    if files:
        try:
            response = requests.get(f"{os.getenv('BACKEND_URL')}/api/auth/connection")
            if response.status_code == 200:
                datas = {
                'batch_id' : os.getenv('BATCH_ID'),
                'microscope_id' : os.getenv('MICROSCOPE_ID'),
            }

            auth = requests.post(f"{os.getenv('BACKEND_URL')}/api/auth/login", json={'username': 'superadmin', 'password': 'password'}).json().get('data').get('token')
            headers = {'Authorization': f'Bearer {auth}'}
            response = requests.post(f"{os.getenv('BACKEND_URL')}/api/cpe/create", data=datas, files=files, headers=headers)
            if response.status_code == 200:
                logging.info('Files uploaded successfully.')

                for _, (filename, _) in files:
                    file_path = os.path.join(folder_path, filename)
                    os.remove(file_path)
                    
                logging.info('Uploaded files deleted.')
            else:
                logging.error(response.json())
                    
        except Exception as e:
            logging.error(f'An error occurred: {str(e)}')