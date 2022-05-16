import asyncio
import threading

from event_handlers import SocketRelayEventHandlers
from socketio import AsyncServer

from .socketio_server import SESSION_IDs


def start_message_sender_thread(
    sio: AsyncServer, event_handlers: SocketRelayEventHandlers, rate_hz: int
) -> threading.Thread:
    """Starts a thread to send messages to the connected SocketIO clients.

    Periodically generates messages using the event handlers and emits
    SocketIO messages.
    """

    async def send_loop():
        async def send_messages():
            if len(SESSION_IDs) > 0:
                for message in event_handlers.generate_messages():
                    await sio.emit(
                        message.event,
                        message.data,
                    )

        while True:
            await asyncio.gather(
                asyncio.sleep(1 / rate_hz),
                send_messages(),
            )

    def thread_fn():
        asyncio.run(send_loop())

    thread = threading.Thread(target=thread_fn)
    thread.start()
    return thread
