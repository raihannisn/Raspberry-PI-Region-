# ML-POLIO-HARDWARE

## Easy Installation (Under Development)

1. chmod +x install.sh
2. ./install.sh

## Manual Installation

1. pip install -r requirements.txt
2. cp .env.example .env
3. update .env file with correct configuration
4. python app.py

## File details for Raspberry Pi

1. install.sh > Easy installation (With Python Environment)
2. app.py > Main raspberry pi script (Loop Check API Version)
    - Slider [DONE]
    - Autofocus [NOT YET]
    - Capture [NOT YET]
3. app_socket.py > Main raspberry pi script (Get signal/trigger from websocket from Backend)
    - Slider [NOT YET]
    - Autofocus [NOT YET]
    - Capture [NOT YET]
4. local_raspy.db > Local SQLite database to store settings value in case Backend is down

## File details for MiniPC

1. broadcast.py > Start automatic broadcast