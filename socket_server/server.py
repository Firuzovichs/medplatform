import socketio
import uvicorn

# Async Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins="*")
app = socketio.ASGIApp(sio)

# --- Socket.IO eventlari ---
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_order_room(sid, data):
    """
    Client ma'lum order room ga qo'shildi.
    """
    order_id = data['order_id']
    room_name = f"order_{order_id}"
    sio.enter_room(sid, room_name)
    print(f"{sid} joined room {room_name}")

@sio.event
async def send_message(sid, data):
    """
    Chat xabarini yuborish
    data = { "order_id": 123, "text": "Salom", "sender": "client" }
    """
    order_id = data['order_id']
    message = data['text']
    sender = data['sender']
    room_name = f"order_{order_id}"
    await sio.emit('new_message', {"text": message, "sender": sender}, room=room_name)
