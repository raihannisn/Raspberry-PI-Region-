from app import socketio
import time

@socketio.on('flag')
def flag(data):
    print('Jalan Perintah Auto Focus')
    print('Received Data:', data)
    time.sleep(1)
    
    # Putar Fokus Rendah Kiri
    print('Putar Fokus Rendah Kiri')
    socketio.emit('rotate-small', 'left')
    time.sleep(1)

    # Putar Forkus Rendah Kanan
    print('Putar Fokus Rendah Kanan')
    socketio.emit('rotate-small', 'right')
    time.sleep(1)

    # DARI AI SUDAH OKE PINDAH KE FOKUS TINGGI
    print('Pindah Fokus Tinggi')
    time.sleep(1)

    # Putar Fokus Tinggi Kiri
    print('Putar Fokus Tinggi Kiri')
    socketio.emit('rotate-big', 'left')
    time.sleep(1)

    # Putar Forkus Tinggi Kanan
    print('Putar Forkus Tinggi Kanan')
    socketio.emit('rotate-big', 'right')
    time.sleep(1)

    # emit OK
    print('Auto Focus Selesai')
    socketio.emit('rotate-finish', True)
    time.sleep(1)