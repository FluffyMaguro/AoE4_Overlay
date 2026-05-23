import asyncio
import json
import threading

import websockets
from websockets.legacy.server import serve as websockets_serve

from overlay.logging_func import get_logger

lock = threading.Lock()
logger = get_logger(__name__)


class Websocket_manager():
    """ Class managing connection through a websocket to the HTML file"""
    def __init__(self, port: int):
        self.port = port
        self.queues = set()
        self.initial_message = None
        self.last_message = None
        self.loop = None

    def run(self):
        self.thread_server = threading.Thread(target=self._start_manager,
                                              daemon=True)
        self.thread_server.start()

    def _start_manager(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            start_server = websockets_serve(self.manager, 'localhost',
                                            self.port)
            self.loop.run_until_complete(start_server)
            self.loop.run_forever()
        except Exception:
            logger.exception("Failed to start manager")

    @staticmethod
    async def _send_ws_message(
            websocket: websockets.legacy.server.WebSocketServerProtocol,
            message):
        message = json.dumps(message)
        await asyncio.wait_for(asyncio.gather(websocket.send(message)),
                               timeout=1)

    async def _broadcast(self, message):
        """ Internal method to put message into all client queues """
        with lock:
            queues = list(self.queues)
        for q in queues:
            q.put_nowait(message)

    async def manager(
            self, websocket: websockets.legacy.server.WebSocketServerProtocol,
            path: str):
        """ Manages websocket connection for each client """
        logger.info(f"Opening: {websocket}")

        q = asyncio.Queue()
        with lock:
            self.queues.add(q)
            # Send the first one (init) and last one message if there is one
            if self.initial_message:
                q.put_nowait(self.initial_message)
            if self.last_message and self.last_message != self.initial_message:
                q.put_nowait(self.last_message)

        try:
            while True:
                message = await q.get()
                try:
                    await self._send_ws_message(websocket, message)
                except asyncio.TimeoutError:
                    logger.warning('Websocket message was timed-out.')
                except Exception:
                    raise

        except (websockets.exceptions.ConnectionClosedOK,
                websockets.exceptions.ConnectionClosedError,
                websockets.exceptions.ConnectionClosed):
            logger.warning('Websocket connection closed.')
        except Exception:
            logger.exception("Error in websocket manager loop")
        finally:
            with lock:
                self.queues.remove(q)

    def send(self, message):
        """ Send message throught a websocket """
        with lock:
            if self.initial_message is None:
                self.initial_message = message
            self.last_message = message

            if self.loop:
                self.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self._broadcast(message)))
