import keyboard
import requests
import time
import RPi.GPIO as GPIO
import json
import http.client

limit_r  = 18   #masukkan pin limit kanan
limit_l  = 18   #masukkan pin limit kiri
en_pin   = 24   #masukkan pin Enable
dir_pin  = 22   #masukkan direction pin
step_pin = 23   #masukkan step pin


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
delays = 0
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

end_point = 'http://bio.official-jsr.com'
headers = {"SECRET-KEY": 'bio123'}

current_pos = 0
prev_pos    = 0

i, pos_max, pos_min, direction = 0, 0, 0, 0

def send_position(post_data):
    apis = '/pages/update_region_api'
    api_endpoint = end_point + apis
    response = requests.post(api_endpoint, json=post_data, headers=headers)
    
    # Check if the request was successful (status code 2xx)
    response.raise_for_status()
    
    # Return the response from the external API
    return response.json()
            
def calibrate():
    print('Calibrate ON!')
    
    global pos_max, reg_1, reg_2, reg_3, reg_4, reg_5, regions
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

def apicall():
    try:
        global ids, arah, arahauto, metode, delays, delays, steps, location, step_region, arah_region, run_region, calibrates, run, delay_auto, starts

        apis = "/api/info/status"
        api_url = end_point + apis
        
        # Make an HTTP GET request
        response = requests.get(api_url,headers=headers)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract and print various fields from the JSON response
            ids = data.get("id")
            arah = data.get("arah")
            starts = data.get("start")
            arahauto = data.get("arah_auto")
            metode = data.get("metode")
            delays = data.get("delay")
            delays = delays/1000
            steps = data.get("step")
            location = data.get("location")
            step_region = data.get("step_region")
            arah_region = data.get("arah_region")
            run_region = data.get("run_region")
            calibrates = data.get("calibrate")
            run = data.get("run")
            delay_auto = (data.get("delay_auto"))/1000

            print("arahAuto:", arahauto)
            print("Start:", starts)
            print("Id:", ids)
            print("arah:", arah)
            print("metode:", metode)
            print("delay:", delays)
            print("step:", steps)
            print("step region:", step_region)
            print("arah region:", arah_region)
            print("run region:", run_region)
            print("calibrate:", calibrates)
            print("delay auto:", delay_auto)
            print(" ")
            
            return data
        else:
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def reset_calibrate():
    url = "/pages/reset_calibrate"
    url = end_point + url
    try:
        response = requests.get(url,headers=headers)
        # Print the HTTP status code
        print("HTTP Code:", response.status_code)
    except requests.RequestException as e:
        print(f"Error making request: {e}")

def reset_arah():
    endpoint = "/pages/reset"
    api_url = end_point + endpoint
    response = requests.get(api_url,headers=headers)

def reset_auto_plus():
    endpoint = "/pages/arah_auto_satu"
    api_url = end_point + endpoint
    response = requests.get(api_url,headers=headers)

def reset_auto_minus():
    endpoint = "/pages/arah_auto_min_satu"
    api_url = end_point + endpoint
    response = requests.get(api_url,headers=headers)

def reset_run_region():
    endpoint = "/pages/reset_location"
    api_url = end_point + endpoint
    response = requests.get(api_url,headers=headers)

def reset_metode():
    endpoint = "/pages/reset_location"
    api_url = end_point + endpoint
    response = requests.get(api_url,headers=headers)

def reset_all_region():
    endpoint = "/pages/reset_all"
    api_url = end_point + endpoint
    response = requests.get(api_url,headers=headers)

def status_minipc():
    endpoint = "/pages/status_mini_pc"
    api_url = end_point + endpoint
    response = requests.get(api_url,headers=headers)

def post_location_awal(nilai):
    endpoint = "/pages/update_region_api"
    api_url = end_point + endpoint
    data = {"region": nilai}
    response = requests.post(api_url, data=data,headers=headers)
    print("HTTP Response code:", response.status_code)

def post_location_baru(nilai):
    endpoint = "/pages/update_location"
    api_url = end_point + endpoint
    data = {"location": nilai}
    response = requests.post(api_url, data=data,headers=headers)
    print("HTTP Response code:", response.status_code)


calibrate()
reset_calibrate()
while True:
    ## Request API
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(limit_r, GPIO.IN)
    GPIO.setup(limit_l, GPIO.IN)
    GPIO.setup(en_pin, GPIO.OUT)
    GPIO.setup(dir_pin, GPIO.OUT)
    GPIO.setup(step_pin, GPIO.OUT)
    apicall()
    if (calibrates == 1):
        calibrate()
        reset_calibrate()
        GPIO.output(en_pin, 1)

    if (starts == 1):
        if (metode == 1):
            #Mode Auto, pada phase II mode auto akan bergerak secara multi region
            
            #reset posisi
            arahreset = int(arahauto)                #start mode auto
            if (arahreset == 1):
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
                        i = i +1
                        
                    else:
                        reset_auto_minus()
                        post_location_baru(pos_max)
                        print("Reset max pos done!")
                        GPIO.output(en_pin, 1)
                        break

            elif (arahreset == -1):
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
            ##opsi untuk melakukan multi region secara terbalik
            GPIO.output(en_pin, 1)
            time.sleep(1)
            
            apicall()
            arahauto = int(arahauto)
            if (arahauto == 1):
                print('mulai dari region 1')
                y = 0
                for y in range(5):
                    i = 0
                    apicall()
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
                    apicall()
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

        elif (metode == 0):
            i = 0
            if (arah == -1):
                apicall()
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

            if (arah == 1):
                apicall()
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

        elif (metode == 2):
            print("Bergerak berdasarkan Region")
            i = 0

            if (arah_region == 1):
                apicall()
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
                apicall()
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
    GPIO.cleanup()
    time.sleep(1)