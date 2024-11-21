import socketio
import atexit
import os
import cv2
import asyncio
import json
import requests
import time
from av import VideoFrame
from threading import Thread
from dotenv import load_dotenv
from aiortc import (
    RTCPeerConnection,
    RTCIceServer,
    RTCConfiguration,
    VideoStreamTrack,
    RTCSessionDescription,
)

load_dotenv()

camera = cv2.VideoCapture(0)
sio = socketio.Client()
batch_id = os.getenv("BATCH_ID")
microscope_id = os.getenv("MICROSCOPE_ID")
configuration = RTCConfiguration([RTCIceServer(urls="turn:wearedollies.com:60004", username="biofarma", credential="biofarma123")])
# configuration = RTCConfiguration([RTCIceServer(urls="stun:stun.l.google.com:19302")])
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
pcs = {}
remote_descriptions = {}
tasks = {}


def connect_websocket():
    while True:
        try:
            if not sio.connected:
                print(os.getenv("WEBSOCKET_URL"))
                sio.connect(os.getenv("WEBSOCKET_URL"))
                print("WebSocket connected.")
        except Exception as e:
            print(f"Failed to connect to WebSocket")

        time.sleep(10)

class CameraVideoStreamTrack(VideoStreamTrack):
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera = camera
        self.counter = 0

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Failed to capture frame from the camera")

        frame = VideoFrame.from_ndarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), format="rgb24")
        frame.pts = pts
        frame.time_base = time_base

        self.counter += 1
        return frame

async def run(session_id):
    global remote_descriptions, pcs, tasks
    pc = pcs[session_id]

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("open")
        def on_datachannel_open():
            print("Data channel is open and connected.")

        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                if channel.readyState == "open":
                    channel.send("pong" + message[4:])
                else:
                    print("Data channel is not in the 'open' state. Current state:", channel.readyState)

    pc.createDataChannel(session_id)

    def on_ice_candidate(candidate):
        pc.addIceCandidate(candidate)

    pc.on("icecandidate")(on_ice_candidate)

    @pc.on("iceconnectionstatechange")
    def on_iceconnectionstatechange():
        print("ICE connection state is", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            print("ICE connection failed.")
            stop_event_loop_and_cleanup(session_id)

    pc.addTrack(CameraVideoStreamTrack(camera_index=0))

    await pc.setLocalDescription(await pc.createOffer())
    sio.emit("offer", {
        'batch_id' : batch_id,
        'microscope_id' : microscope_id,
        'data' : json.dumps(pc.localDescription.__dict__)
    })
    # print(json.dumps(pc.localDescription.__dict__))

    while session_id not in remote_descriptions:
        await asyncio.sleep(1)
    # print(f'{remote_descriptions[session_id]}') 
    await pc.setRemoteDescription(remote_descriptions[session_id])

    while session_id not in tasks:
        await asyncio.sleep(1)

@sio.on(f'answer-{batch_id}-{microscope_id}')
def receive_answer(data):
    global remote_descriptions
    remote_descriptions[str(data['session'])] = RTCSessionDescription(**json.loads(data['data']))

@sio.on(f'order-{batch_id}-{microscope_id}')
def make_order(data):
    global pcs, remote_descriptions, tasks, loop
    session_id = str(data['session'])

    if session_id in pcs:
        pc = pcs[session_id]
        pc.close()
        del pcs[session_id]

    if session_id in remote_descriptions:
        del remote_descriptions[session_id]

    if session_id in tasks:
        tasks[session_id].cancel()
        del tasks[session_id]

    pcs[session_id] = RTCPeerConnection(configuration=configuration)
    task = loop.create_task(run(session_id))
    loop.run_until_complete(task)
    tasks[session_id] = task

@sio.on(f'setting-{batch_id}-{microscope_id}')
def update_setting(data):
    requests.post(f"{os.getenv('APP_URL')}/settings/update", json=data)
    sio.emit(f'setting-uptodate', {
        'batch_id': batch_id,
        'microscope_id': microscope_id,
        'result': True
    })

def disconnect_socket_io():
    if sio.connected:
        sio.disconnect()

def stop_event_loop_and_cleanup(session_id):
    global tasks
    if session_id in tasks:
        tasks[session_id].cancel()
        del tasks[session_id]

atexit.register(disconnect_socket_io)
websocket_thread = Thread(target=connect_websocket)
websocket_thread.daemon = True
websocket_thread.start()