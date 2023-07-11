from flask_socketio import emit
from ..socketio import bp, socketio


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    with open('logs.log', 'r') as f:
        logs = f.read()
    emit('logs', logs)


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('logs')
def handle_logs():
    print('Client Logging')
    with open('logs.log', 'r') as f:
        logs = f.readlines()[-1]
    emit('logs', logs)
