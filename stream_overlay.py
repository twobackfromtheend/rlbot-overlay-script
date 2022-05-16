import asyncio

from loguru import logger
from rlbot.socket.socket_manager_asyncio import SocketRelayAsyncio

import server.sanic_server as sanic_server
from event_handlers import SocketRelayEventHandlers
from server.sender_thread import start_message_sender_thread
from server.socketio_server import sio


class OverlayScript:
    def __init__(self):
        self.socket_relay = SocketRelayAsyncio()
        self.event_handlers = SocketRelayEventHandlers()

    def run(self):
        logger.info("Running overlay script")
        self.event_handlers.hook_handlers(self.socket_relay)
        logger.info("Hooked handlers")

        relay_coroutine = self.socket_relay.connect_and_run(
            wants_quick_chat=True,
            wants_game_messages=True,
            wants_ball_predictions=False,
        )
        asyncio.get_event_loop().create_task(relay_coroutine)
        logger.info("Started relay coroutine")

        thread = start_message_sender_thread(sio, self.event_handlers, rate_hz=30)
        logger.info("Started message sending thread")
        # TODO: Does this need to be started after the sanic server?

        app = sanic_server.attach_socketio_server_to_app(sio)
        logger.info("Attached SocketIO server to app")
        sanic_server.start_server(app)
        logger.info("Overlay script run ended")


if __name__ == "__main__":
    from utils import setup_loguru

    print("Socket script starting...")
    setup_loguru()
    OverlayScript().run()
