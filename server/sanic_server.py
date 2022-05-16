import asyncio

import socketio
from loguru import logger
from sanic import Sanic
from sanic.server import AsyncioServer
from sanic_cors import CORS


def attach_socketio_server_to_app(socketio_server: socketio.AsyncServer) -> Sanic:
    """
    See: https://python-socketio.readthedocs.io/en/latest/server.html#sanic
    """
    app = Sanic(name="rlbot_overlay")
    app.config["CORS_SUPPORTS_CREDENTIALS"] = True
    CORS(app)
    socketio_server.attach(app)
    return app


def start_server(app: Sanic):
    """
    See: https://github.com/sanic-org/sanic/blob/main/examples/run_async_advanced.py
    """
    loop = asyncio.get_event_loop()

    server_coroutine = app.create_server(
        port=8000,
        return_asyncio_server=True,
        # debug=True
    )
    server_task = asyncio.ensure_future(server_coroutine, loop=loop)
    server: AsyncioServer = asyncio.get_event_loop().run_until_complete(server_task)
    loop.run_until_complete(server.startup())

    loop.run_until_complete(server.before_start())
    loop.run_until_complete(server.after_start())
    try:
        logger.info("Running Sanic server...")
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.run_until_complete(server.before_stop())

        # Wait for server to close
        logger.info("Waiting for Sanic server to close...")
        close_task = server.close()
        loop.run_until_complete(close_task)

        # Complete all tasks on the loop
        for connection in server.connections:
            connection.close_if_idle()
        loop.run_until_complete(server.after_stop())
        logger.info("Sanic server closed.")


__all__ = ["attach_socketio_server_to_app", "start_server"]

if __name__ == "__main__":
    from socketio_server import sio

    # import sys
    # logger.remove()
    # logger.add(sys.stderr, level="DEBUG")

    app = attach_socketio_server_to_app(sio)

    async def hi():
        while True:
            await sio.emit("hi", {"data": 1})
            await asyncio.sleep(1)

    asyncio.get_event_loop().create_task(hi())
    start_server(app)
