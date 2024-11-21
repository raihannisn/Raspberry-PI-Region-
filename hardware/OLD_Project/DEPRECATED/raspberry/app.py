from flask import Flask, jsonify
import socketio
import time

app = Flask(__name__)
sio = socketio.Client()
sio.connect('http://127.0.0.1:5000')

# SLIDER OFF
@app.route('/flag', methods=['GET']) #Hapus
def get_items():
    print('perintah auto focus')
    sio.emit("flag", True)
    return jsonify({'status': True}) # HAPUS

# AUTO FOCUS HW FOKUS RENDAH
@sio.on(f'rotate-small')
def receive_answer(data):
    if data == 'left':
        print('fokus rendah putar kiri')
    else:
        print('fokus rendah kanan')
    time.sleep(1)

# AUTO FOCUS HW FOKUS TINGGI
@sio.on(f'rotate-big')
def receive_answer(data):
    if data == 'left':
        print('fokus tinggi putar kiri')
        # delay 10 second, and then send signal to server
        # time.sleep(10)
        # sio.emit("flag", False)
    else:
        print('fokus tinggi putar kanan')
    time.sleep(1)

# SLIDER ON
@sio.on(f'rotate-finish')
def receive_answer(data):
    time.sleep(1)
    print('motor Jalan')

if __name__ == '__main__':
    app.run(debug=True)
