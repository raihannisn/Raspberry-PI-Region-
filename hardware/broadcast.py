from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import os
from dotenv import load_dotenv
import time
import pyautogui

load_dotenv()

api_endpoint = os.getenv('API_URL')  # Ubah sesuai dengan domain backend
api_key = os.getenv('API_KEY')  # Ubah sesuai dengan API Key yang didapat dari backend
serial_number = os.getenv('MICROSCOPE_SERIAL_NUMBER') # Ubah sesuai dengan serial number mikroskop yang ingin diakses

url = f"{api_endpoint}/cloud/broadcast?serial_number={serial_number}"

print('[!] Connecting to API to get broadcast link...')
print('[*] URL:', url)

try:
    response = requests.get(url, headers={'X-API-Key': api_key})
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    broadcast = data.get('result')
    if not broadcast:
        raise ValueError("Broadcast link not found in API response.")
    print('[*] Broadcast link:', broadcast)

    options = Options()
    #! options.add_argument("--use-fake-ui-for-media-stream")
    #! options.add_argument("--enable-usermedia-screen-capturing")

    # Use DevTools Protocol to select screen capture source
    #! options.add_experimental_option('excludeSwitches', ['enable-automation'])
    #! options.add_experimental_option('useAutomationExtension', False)
    #! options.add_argument('--disable-blink-features=AutomationControlled')
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    
    print('[!] Opening browser...')
    driver.get(broadcast)

    time.sleep(3)

    pyautogui.press('tab')
    pyautogui.press('right')
    pyautogui.press('tab')
    pyautogui.press('right')
    pyautogui.press('right')
    pyautogui.press('enter')

    time.sleep(3)

    # Menunggu input dari pengguna sebelum menutup browser
    input("Press any key to close the browser...")
finally:
    # Menutup browser
    driver.quit()