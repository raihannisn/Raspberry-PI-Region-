from flask import request, jsonify
from app import app, db
from app.models import Setting
from app.schemas import SettingUpdateSchema
from dotenv import load_dotenv
import time
import os
import requests
load_dotenv()

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/api/cpe', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'status':False,'message': 'No file part','data':{}}), 400
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'status':False,'message': 'No selected file','data':{}}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'status':False,'message': 'Invalid file extension','data':{}}), 400

    inputs = request.get_json() if request.content_type == 'application/json' else request.form.to_dict()

    if 'region' in inputs :
        if int(inputs['region']) not in [1,2,3,4,5]:
            return jsonify({'status':False,'message': 'Invalid Input region','data':{}}), 400
    else:
        return jsonify({'status':False,'message': 'region Required','data':{}}), 400

    if 'type' in inputs  :
        if inputs['type'] not in ['single', 'multi']:
            return jsonify({'status':False,'message': 'Invalid Input type','data':{}}), 400

        if inputs['type'] == 'multi':
            filename = 'M_' + inputs['region'] + '_' + os.getenv('BATCH_ID') + '_' + os.getenv('MICROSCOPE_ID') + '_' + str(time.time()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        else:
            filename = 'S_' + inputs['region'] + '_' + os.getenv('BATCH_ID') + '_' + os.getenv('MICROSCOPE_ID') + '_' + str(time.time()) + '.' + file.filename.rsplit('.', 1)[1].lower()
    else:
        return jsonify({'status':False,'message': 'type Required','data':{}}), 400

    try:
        response = requests.get(f"{os.getenv('BACKEND_URL')}/api/auth/connection")
        if response.status_code == 200:
            datas = {
                'batch_id' : os.getenv('BATCH_ID'),
                'microscope_id' : os.getenv('MICROSCOPE_ID'),
            }
            files = [('images[]',(filename, file))]

            auth = requests.post(f"{os.getenv('BACKEND_URL')}/api/auth/login", json={'username': 'superadmin', 'password': 'password'}).json().get('data').get('token')
            headers = {'Authorization': f'Bearer {auth}'}
            upload = requests.post(f"{os.getenv('BACKEND_URL')}/api/cpe/create", data=datas, files=files, headers=headers)
            return jsonify({'status':True,'message': 'Success Post CPE Capture','data':{}}), 200
        
    except Exception as e:
        upload_folder = 'storage/cpe'

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        uploaded_file_path = os.path.join(upload_folder, filename)
        file.save(uploaded_file_path)

        return jsonify({'status':True,'message': 'Not Connected to Cloud, Data Save to Local','data':{}}), 200

    return jsonify({'status':True})

@app.route('/api/settings', methods=['GET'])
def get_items():
    item = Setting.query.first()
    if item:
        return jsonify({'status':True,'message':'Success','data':item.as_dict()}), 200
    else:
        return jsonify({'status':False,'message':'Not Found','data':{}}), 404

@app.route('/api/settings/update', methods=['POST'])
def update_item():
    schema = SettingUpdateSchema()
    inputs = request.get_json() if request.content_type == 'application/json' else request.form.to_dict()
    try:
        datas = schema.load(inputs)
    except Exception as e:
        return jsonify({'status':False,'message': 'Validation errors', 'data': str(e)}), 422
    item = Setting.query.first()
    if not item:
        new_setting = Setting(**datas)
        db.session.add(new_setting)
        db.session.commit()
    else:
        for key, value in datas.items():
            setattr(item, key, value)
    
    db.session.commit()
    db.session.refresh(item)

    try:
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
        setattr(item, 'is_uptodate', False)
        db.session.commit()

    return jsonify({'status':True,'message':'Success','data':{}}), 200

@app.route('/settings/update', methods=['POST'])
def update_setting():
    schema = SettingUpdateSchema()
    inputs = request.get_json() if request.content_type == 'application/json' else request.form.to_dict()
    try:
        datas = schema.load(inputs)
    except Exception as e:
        return jsonify({'status':False,'message': 'Validation errors', 'data': str(e)}), 422
    item = Setting.query.first()
    if not item:
        new_setting = Setting(**datas)
        db.session.add(new_setting)
        db.session.commit()
    else:
        for key, value in datas.items():
            setattr(item, key, value)
    
    db.session.commit()
    return jsonify({'status':True,'message':'Success','data':{}}), 200