# Main script

from flask import Flask, jsonify
import socketio
import sqlite3
from datetime import datetime
import requests
import os
import RPi.GPIO as GPIO
import json
import http.client
from dotenv import load_dotenv
import time
from threading import Thread
import keyboard

load_dotenv()

app = Flask(__name__)
sio = socketio.Client()
sio.connect(os.getenv('WEBSOCKET_URL'))

limit_r  = os.getenv('LIMIT_R')         #masukan pin limit kanan
limit_l  = os.getenv('LIMIT_L')         #masukan pin limit kiri
en_pin   = os.getenv('EN_PIN')          #masukan pin Enable
dir_pin  = os.getenv('DIR_PIN')         #masukan direction pin
step_pin = os.getenv('STEP_PIN')        #masukan step pin

arahauto = 0
starts = 0
ids = 0
arah = 0
metode = 0
delays = 0
steps = 0
step_region = 0
arah_region = 0
run_region = 0
calibrates = 0
location = 0
run = 0
delay_auto = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(limit_r, GPIO.IN)
GPIO.setup(limit_l, GPIO.IN)
GPIO.setup(en_pin, GPIO.OUT)
GPIO.setup(dir_pin, GPIO.OUT)
GPIO.setup(step_pin, GPIO.OUT)
GPIO.output(en_pin, 1)

endpoint = os.getenv('API_URL')
headers = {"X-API-Key": os.getenv('API_KEY')}

current_pos = 0
prev_pos    = 0
i, pos_max, pos_min, direction = 0, 0, 0, 0
microscope_sn = os.getenv('MICROSCOPE_SERIAL_NUMBER')
microscope = None
batch = None

# index
@app.route('/', methods=['GET']) #Hapus
def get_index():
    return jsonify({'status': True}) # HAPUS

def all_status():
    global arahauto, starts, ids, arah, metode, delays, steps, step_region, arah_region, run_region, calibrates, location, run, delay_auto
    api = endpoint + '/formicroscope/status'
    data = {'microscope_id': microscope['id'], 'batch_id': batch['id']}
    response = requests.get(api, headers=headers, params=data)
    if response.status_code == 200:
        result = response.json()['result']
        arahauto = int(result['arah_auto'])
        starts = int(result['start'])
        ids = int(result['id'])
        arah = int(result['arah'])
        metode = int(result['metode'])
        delays = int(result['delay'])
        steps = int(result['step'])
        step_region = int(result['step_region'])
        arah_region = int(result['arah_region'])
        run_region = int(result['location'])
        calibrates = int(result['calibrate'])
        location = int(result['location'])
        run = int(result['run'])
        delay_auto = int(result['delay_auto'])
        print(f"[INFO] All status updated.")

        conn = sqlite3.connect('local_raspy')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS settings")
        cursor.execute("CREATE TABLE IF NOT EXISTS settings (arah_auto INTEGER, start INTEGER, id INTEGER, arah INTEGER, metode INTEGER, delay INTEGER, step INTEGER, step_region INTEGER, arah_region INTEGER, run_region INTEGER, calibrate INTEGER, delay_auto INTEGER, location INTEGER, run INTEGER)")
        cursor.execute(f"INSERT INTO settings (arah_auto, start, id, arah, metode, delay, step, step_region, arah_region, run_region, calibrate, delay_auto, location, run) VALUES ({arahauto}, {starts}, {ids}, {arah}, {metode}, {delays}, {steps}, {step_region}, {arah_region}, {run_region}, {calibrates}, {delay_auto}, {location}, {run})")
        conn.commit()
        conn.close()
    else:
        print(f"[ERROR] Failed to update all status.")

def update_status(data):
    global arahauto, starts, ids, arah, metode, delays, steps, step_region, arah_region, run_region, calibrates, location, run, delay_auto
    result = data
    arahauto = int(result['arah_auto'])
    starts = int(result['start'])
    ids = int(result['id'])
    arah = int(result['arah'])
    metode = int(result['metode'])
    delays = int(result['delay'])
    steps = int(result['step'])
    step_region = int(result['step_region'])
    arah_region = int(result['arah_region'])
    run_region = int(result['location'])
    calibrates = int(result['calibrate'])
    location = int(result['location'])
    run = int(result['run'])
    delay_auto = int(result['delay_auto'])
    print(f"[INFO] All status updated via socket.")

    conn = sqlite3.connect('local_raspy')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS settings")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (arah_auto INTEGER, start INTEGER, id INTEGER, arah INTEGER, metode INTEGER, delay INTEGER, step INTEGER, step_region INTEGER, arah_region INTEGER, run_region INTEGER, calibrate INTEGER, delay_auto INTEGER, location INTEGER, run INTEGER)")
    cursor.execute(f"INSERT INTO settings (arah_auto, start, id, arah, metode, delay, step, step_region, arah_region, run_region, calibrate, delay_auto, location, run) VALUES ({arahauto}, {starts}, {ids}, {arah}, {metode}, {delays}, {steps}, {step_region}, {arah_region}, {run_region}, {calibrates}, {delay_auto}, {location}, {run})")
    conn.commit()
    conn.close()

def get_microscope():
    global microscope

    print(f"[INFO] Getting microscope ({microscope_sn}) data...")
    api = endpoint + '/cloud/microscope/find/'
    data = {'serial_number': microscope_sn}
    response = requests.get(api, headers=headers, params=data)
    microscope = response.json()['result']
    if (microscope['id']):
        print(f"[INFO] Microscope data found, microscope name: {microscope['name']}.")
        return microscope
    else:
        print("[ERROR] Microscope data not found, please check your microscope serial number.")
        exit()

def get_batch():
    global batch

    print(f"[INFO] Getting active batch for microscope ({microscope['name']})...")
    api = endpoint + '/cloud/batch/find/'
    data = {'microscope_id': microscope['id']}
    response = requests.get(api, headers=headers, params=data)
    batch = response.json()['result']
    if (batch['id']):
        print(f"[INFO] Batch data found, batch number: {batch['number']}.")
        return batch
    else:
        print("[ERROR] Batch data not found, please check your batch id.")
        exit()

def update_data(key, value):
    global microscope, batch

    api = endpoint + '/formicroscope/update'
    data = {
        'batch_id': batch['id'],
        'microscope_id': microscope['id']
    }

    for i in range(len(key)):
        data[key[i]] = value[i]

    response = requests.post(api, headers=headers, data=data)
    if response.status_code == 200:
        return f"[SUCCESS] {key} updated to {value}."
    else:
        return f"[ERROR] Failed to update {key}."

def calibrate():
    global pos_max, reg_1, reg_2, reg_3, reg_4, reg_5, regions
    
    print('[INFO] Calibrating microscope...')
    i = 0
    GPIO.output(dir_pin, 0)
    GPIO.output(en_pin, 0)
    for i in range(100000):
        det = GPIO.input(limit_l)
        if (det == 1):
            GPIO.output(step_pin, 1) # set value high untuk pin step
            time.sleep(0.01)
            GPIO.output(step_pin, 0) # set value low untuk pin step
            time.sleep(0.01)
            i += 1
        else:
            i = 100000+1
    GPIO.output(en_pin, 1)
        

    time.sleep(1)

    i = 0
    GPIO.output(dir_pin, 1)
    GPIO.output(en_pin, 0)
    for i in range(100000):
        det = GPIO.input(limit_r)
        if (det == 1):
            GPIO.output(step_pin, 1) # set value high untuk pin step
            time.sleep(0.01)
            GPIO.output(step_pin, 0) # set value low untuk pin step
            time.sleep(0.01)
            pos_max = pos_max +1
            #print(pos_max)
        else:
            
            i = 100000+1
    GPIO.output(en_pin, 1)

    ranges = pos_max - pos_min
    distance = ranges / 5
    t = distance / 2

    reg_1 = pos_min + t
    reg_2 = reg_1 + distance
    reg_3 = reg_2 + distance
    reg_4 = reg_3 + distance
    reg_5 = reg_4 + distance
    regions = [reg_1, reg_2, reg_3, reg_4, reg_5]
    print(regions)

    time.sleep(1)
    i = 0
    GPIO.output(dir_pin, 0)
    GPIO.output(en_pin, 0)
    for i in range(int(distance)):
        GPIO.output(step_pin, 1) # set value high untuk pin step
        time.sleep(0.01)
        GPIO.output(step_pin, 0) # set value low untuk pin step
        time.sleep(0.01)
        i += 1

    post_location_awal(reg_3)
    post_location_baru(reg_3)
    GPIO.output(en_pin, 1)

def reset_calibrate():
    print("[INFO] Resetting calibrate...")
    print(update_data(['calibrate'], [0]))

def reset_arah():
    print("[INFO] Resetting arah...")
    print(update_data(['arah'], [0]))

def reset_auto_plus():
    print("[INFO] Resetting auto plus...")
    print(update_data(['arah_auto'], [1]))

def reset_auto_minus():
    print("[INFO] Resetting auto minus...")
    print(update_data(['arah_auto'], [-1]))

def reset_run_region():
    print("[INFO] Resetting run region...")
    print(update_data(['location'], [0]))

def reset_metode():
    print("[INFO] Resetting metode...")
    print(update_data(['location'], [0]))

def reset_all_region():
    print("[INFO] Resetting all region...")
    print(update_data(['arah_region', 'metode', 'step_region', 'calibrate'], [0, 0, 0, 0]))

def post_location_awal(nilai):
    api = endpoint + '/formicroscope/update_region_api'
    data = {"region": nilai}
    response = requests.post(api, headers=headers, data=data)
    if response.status_code == 200:
        print(f"[SUCCESS] All region value updated.")
    else:
        print(f"[ERROR] Failed to update location.")

def post_location_baru(nilai):
    print("[INFO] Update new location...")
    print(update_data(['location'], [nilai]))

@sio.on(f'test')
def receive_test(data):
    print(f"data {data}")

    sio.emit('test-callback', {'data': 'test'})

@sio.on(f'ms-update')
def receive_update(data):
    print(f"[SOCKET] Received update data: {data}.")
    microscope_serial_number = data['microscope_serial_number']

    if (microscope_serial_number == microscope_sn):
        update_status(data['data'])
        sio.emit('update-callback', {
            'microscope_serial_number': microscope_serial_number,
            'microscope_id': microscope['id'],
            'data': 'update success'
        })

@sio.on(f'ms-calibrate')
def receive_calibrate(data):
    print(f"[SOCKET] Received calibrate data: {data}.")
    microscope_serial_number = data['microscope_serial_number']

    if (microscope_serial_number == microscope_sn):
        update_status(data['data'])
        calibrate()
        reset_calibrate()
        GPIO.output(en_pin, 1)

@sio.on(f'ms-multi_region_capture')
def receive_multi_region_capture(data):
    print(f"[SOCKET] Received multi region capture data: {data}.")
    microscope_serial_number = data['microscope_serial_number']

    if (microscope_serial_number == microscope_sn):
        update_status(data['data'])
        if (True):
            pass
        else:
            pass

@sio.on(f'ms-manual_move_step')
def receive_manual_move_step(data):
    print(f"[SOCKET] Received manual move step data: {data}.")
    microscope_serial_number = data['microscope_serial_number']

    if (microscope_serial_number == microscope_sn):
        i = 0
        update_status(data['data'])
        if (arah == -1):
            loc = location
            GPIO.output(dir_pin, 0)
            GPIO.output(en_pin, 0)
            for i in range(steps):
                limitLeft = GPIO.input(limit_l)
                limitRight = GPIO.input(limit_r)
                if (limitLeft == 0):
                    j = i
                    i = steps+1
                    post_location_baru(pos_min)
                    break
                else:
                    GPIO.output(en_pin, 0)
                    GPIO.output(step_pin, 1)
                    time.sleep(delays)
                    GPIO.output(step_pin, 0)
                    time.sleep(delays)
                if (i == steps):
                    i_post = loc - steps
                    post_location_baru(i_post)
            GPIO.output(en_pin, 1)
            reset_arah()
        else:
            loc = location
            GPIO.output(dir_pin, 1)
            GPIO.output(en_pin, 0)
            for i in range(steps):
                limitLeft = GPIO.input(limit_l)
                limitRight = GPIO.input(limit_r)
                if (limitRight == 0):
                    j = i
                    i = steps+1
                    post_location_baru(pos_max)
                    break
                else:
                    GPIO.output(en_pin, 0)
                    GPIO.output(step_pin, 1)
                    time.sleep(delays)
                    GPIO.output(step_pin, 0)
                    time.sleep(delays)
                if (i == steps):
                    i_post = loc + steps
                    post_location_baru(i_post)
            GPIO.output(en_pin, 1)
            reset_arah()

@sio.on(f'ms-manual_move_region')
def receive_manual_move_region(data):
    print(f"[SOCKET] Received manual move region data: {data}.")
    microscope_serial_number = data['microscope_serial_number']

    if (microscope_serial_number == microscope_sn):
        i = 0
        update_status(data['data'])
        if (arah_region == 1):
            loc = location
            GPIO.output(dir_pin, 1)
            GPIO.output(en_pin, 0)
            for i in range(step_region):
                limitLeft = GPIO.input(limit_l)
                limitRight = GPIO.input(limit_r)
                if (limitRight == 0):
                    j = i
                    i = step_region+1
                    post_location_baru(pos_max)
                else:
                    GPIO.output(en_pin, 0)
                    GPIO.output(step_pin, 1)
                    time.sleep(delays)
                    GPIO.output(step_pin, 0)
                    time.sleep(delays)
                if (i == step_region):
                    i_post = loc+step_region
                    post_location_baru(i_post)
                    GPIO.output(en_pin, 1)
            reset_all_region()
        elif (arah_region == -1):
            loc = location
            GPIO.output(dir_pin, 0)
            GPIO.output(en_pin, 0)
            for i in range(step_region):
                limitLeft = GPIO.input(limit_l)
                limitRight = GPIO.input(limit_r)
                if (limitLeft == 0):
                    j = i
                    i = step_region+1
                    post_location_baru(0)
                else:
                    GPIO.output(en_pin, 0)
                    GPIO.output(step_pin, 1)
                    time.sleep(delays)
                    GPIO.output(step_pin, 0)
                    time.sleep(delays)
                if (i == step_region):
                    i_post = loc-step_region
                    post_location_baru(i_post)
                    GPIO.output(en_pin, 1)
            reset_all_region()
            GPIO.output(en_pin, 1)
        pass

def flask_run():
    app.run(host=os.getenv('FLASK_HOST'), port=os.getenv('FLASK_PORT'), debug=os.getenv('FLASK_DEBUG'), use_reloader=False)

def mode_auto():
    global arahauto, starts, ids, arah, metode, delays, steps, step_region, arah_region, run_region, calibrates, location, run, delay_auto
    if (metode == 1):
        # Mode Auto, pada phase II mode auto akan bergerak secara multi region
        # reset posisi
        if (arahauto == 1):
            GPIO.output(dir_pin, 1)
            GPIO.output(en_pin, 0)
            for i in range(pos_max):
                i = 0
                limitRight = GPIO.input(limit_r)
                if (limitRight == 1):
                    GPIO.output(step_pin, 1)
                    time.sleep(0.01)
                    GPIO.output(step_pin, 0)
                    time.sleep(0.01)
                    i = i + 1
                else:
                    reset_auto_minus()
                    post_location_baru(pos_max)
                    print("Reset max pos done!")
                    GPIO.output(en_pin, 1)
                    break
        elif (arahauto == -1):
            GPIO.output(dir_pin, 0)
            GPIO.output(en_pin, 0)
            for i in range(pos_max):
                i = 0
                limitRight = GPIO.input(limit_r)
                if (limitRight == 1):
                    GPIO.output(step_pin, 1)
                    time.sleep(0.01)
                    GPIO.output(step_pin, 0)
                    time.sleep(0.01)
                    i = i + 1
                    
                else:
                    reset_auto_plus()
                    post_location_baru(pos_min)
                    print("Reset min pos done!")
                    GPIO.output(en_pin, 1)
                    break
        # opsi untuk melakukan multi region secara terbalik
        GPIO.output(en_pin, 1)
        time.sleep(5)
        
        if (arahauto == 1):
            print('mulai dari region 1')
            y = 0
            for y in range(5):
                i = 0
                if (starts == 0) or (metode != 1):
                    break
                i = 0
                loc = location
                stepes = regions[y]-loc
                print(regions[y])
                print(int(stepes))
                GPIO.output(dir_pin, 1)
                GPIO.output(en_pin, 0)
                for i in range(int(stepes)):
                    limitRight = GPIO.input(limit_r)
                    if (limitRight == 0):
                        j = i
                        post_location_baru(pos_max)
                        reset_auto_minus()
                        GPIO.output(en_pin, 1)
                        break
                    else:
                        GPIO.output(en_pin, 0)
                        GPIO.output(step_pin, 1)
                        time.sleep(delays)
                        GPIO.output(step_pin, 0)
                        time.sleep(delays)
                post_location_baru(regions[y])
                print("Auto time delay, please waiting...")
                time.sleep(delay_auto)
                GPIO.output(en_pin, 1)
        elif(arahauto == -1):
            print('mulai dari region 5')
            y = 4
            for y in range(4, -1, -1):
                i = 0
                if (starts == 0) or (metode != 1):
                    break
                i = 0
                loc = location
                stepes = loc-regions[y]
                print(regions[y])
                print(int(stepes))
                GPIO.output(dir_pin, 0)
                GPIO.output(en_pin, 0)
                for i in range(int(stepes)):
                    limitRight = GPIO.input(limit_r)
                    if (limitRight == 0):
                        j = i
                        post_location_baru(pos_min)
                        reset_auto_plus()
                        GPIO.output(en_pin, 1)
                        break
                    else:
                        GPIO.output(en_pin, 0)
                        GPIO.output(step_pin, 1)
                        time.sleep(delays)
                        GPIO.output(step_pin, 0)
                        time.sleep(delays)
                post_location_baru(regions[y])
                print("Auto time delay, please waiting...")
                time.sleep(delay_auto)
                GPIO.output(en_pin, 1)

def slider_setup():
    get_microscope()
    get_batch()
    reset_all_region()
    # calibrate()
    reset_calibrate()
    all_status()
    while True:
        mode_auto()

def sync_status():
    while True:
        all_status()
        time.sleep(60)

def main():
    thread1 = Thread(target=flask_run)
    thread2 = Thread(target=slider_setup)
    thread3 = Thread(target=sync_status)

    thread1.start()
    thread2.start()
    thread3.start()

    # thread1.join()
    # thread2.join()
    # thread3.join()

    while True:
        # If 'esc' is pressed, stop the threads and break the loop
        if keyboard.is_pressed('esc'):
            thread1.join()
            thread2.join()
            thread3.join()
            break

if __name__ == '__main__':
    main()