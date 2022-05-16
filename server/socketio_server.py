import socketio
from loguru import logger

sio = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=[])

SESSION_IDs = set()


@sio.event
def my_event(sid, data):
    pass


@sio.on("my custom event")
def another_event(sid, data):
    pass


@sio.event
async def my_event(sid, data):
    pass


@sio.event
def connect(sid, environ, auth):
    SESSION_IDs.add(sid)
    logger.info(
        f"Client connected to socket: {sid}, {environ}, {auth} \t\t({len(SESSION_IDs)} total)"
    )


@sio.event
def disconnect(sid):
    SESSION_IDs.remove(sid)
    logger.info(
        f"SocketIO client disconnected: {sid} \t\t({len(SESSION_IDs)} remaining)"
    )


__all__ = ["sio", SESSION_IDs]
