#!/bin/bash

echo "██████╗  ██████╗ ██╗     ██╗ ██████╗     ███████╗ █████╗ ███████╗███████╗    ██████╗ "
echo "██╔══██╗██╔═══██╗██║     ██║██╔═══██╗    ██╔════╝██╔══██╗██╔════╝██╔════╝    ╚════██╗"
echo "██████╔╝██║   ██║██║     ██║██║   ██║    █████╗  ███████║███████╗█████╗       █████╔╝"
echo "██╔═══╝ ██║   ██║██║     ██║██║   ██║    ██╔══╝  ██╔══██║╚════██║██╔══╝      ██╔═══╝ "
echo "██║     ╚██████╔╝███████╗██║╚██████╔╝    ██║     ██║  ██║███████║███████╗    ███████╗"
echo "╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝     ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝"
echo "                                                                                     "
echo "--------------------------------HARDWARE SETUP SCRIPT--------------------------------"
echo "                                                                                     "

# Function to prompt user for input
prompt_input() {
    read -p "$1: " input
    echo "$input"
}

FLASK_HOST=$(prompt_input "Enter the host for the Flask server")
FLASK_PORT=$(prompt_input "Enter the port for the Flask server")
FLASK_DEBUG=$(prompt_input "Enter the debug mode for the Flask server (True/False)")
WEBSOCKET_URL=$(prompt_input "Enter the URL for the WebSocket server, with port if applicable")
API_URL=$(prompt_input "Enter the URL for the API server")
API_KEY=$(prompt_input "Enter the API key for the API server")
LIMIT_R=$(prompt_input "Enter the GPIO LIMIT_R pin")
LIMIT_L=$(prompt_input "Enter the GPIO LIMIT_L pin")
EN_PIN=$(prompt_input "Enter the GPIO EN_PIN pin")
DIR_PIN=$(prompt_input "Enter the GPIO DIR_PIN pin")
STEP_PIN=$(prompt_input "Enter the GPIO STEP_PIN pin")
MICROSCOPE_SERIAL_NUMBER=$(prompt_input "Enter the serial number for the microscope")

# Create python environment
python3 -m venv venv

# Activate python environment
source venv/bin/activate

# Install python packages
pip3 install -r requirements.txt

# Deactivate python environment
deactivate

# Create .env file
cp .env.example .env

# Update environment variables
sed -i "s|FLASK_HOST=.*|FLASK_HOST=$FLASK_HOST|" .env
sed -i "s|FLASK_PORT=.*|FLASK_PORT=$FLASK_PORT|" .env
sed -i "s|FLASK_DEBUG=.*|FLASK_DEBUG=$FLASK_DEBUG|" .env
sed -i "s|WEBSOCKET_URL=.*|WEBSOCKET_URL=$WEBSOCKET_URL|" .env
sed -i "s|API_URL=.*|API_URL=$API_URL|" .env
sed -i "s|API_KEY=.*|API_KEY=$API_KEY|" .env
sed -i "s|LIMIT_R=.*|LIMIT_R=$LIMIT_R|" .env
sed -i "s|LIMIT_L=.*|LIMIT_L=$LIMIT_L|" .env
sed -i "s|EN_PIN=.*|EN_PIN=$EN_PIN|" .env
sed -i "s|DIR_PIN=.*|DIR_PIN=$DIR_PIN|" .env
sed -i "s|STEP_PIN=.*|STEP_PIN=$STEP_PIN|" .env
sed -i "s|MICROSCOPE_SERIAL_NUMBER=.*|MICROSCOPE_SERIAL_NUMBER=$MICROSCOPE_SERIAL_NUMBER|" .env

echo "Installation complete"