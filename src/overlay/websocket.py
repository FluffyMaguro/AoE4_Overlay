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
        self.overlay_messages = []
        self.port = port

    def run(self):
        self.thread_server = threading.Thread(target=self._start_manager,
                                              daemon=True)
        self.thread_server.start()

    def _start_manager(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            start_server = websockets_serve(self.manager, 'localhost',
                                            self.port)
            loop.run_until_complete(start_server)
            loop.run_forever()
        except Exception:
            logger.exception("Failed to start manager")

    @staticmethod
    async def _send_ws_message(
            websocket: websockets.legacy.server.WebSocketServerProtocol,
            message):
        message = json.dumps(message)
        await asyncio.wait_for(asyncio.gather(websocket.send(message)),
                               timeout=1)

    async def manager(
            self, websocket: websockets.legacy.server.WebSocketServerProtocol,
            path: str):
        """ Manages websocket connection for each client """
        logger.info(f"Opening: {websocket}")

        # Send the first one (init) and last one message if there is one
        if self.overlay_messages:
            await self._send_ws_message(websocket, self.overlay_messages[0])
            if self.overlay_messages[0] != self.overlay_messages[-1]:
                await self._send_ws_message(websocket,
                                            self.overlay_messages[-1])

        sent = len(self.overlay_messages)

        while True:
            try:
                if len(self.overlay_messages) == sent:
                    continue
                await self._send_ws_message(websocket,
                                            self.overlay_messages[sent])
                sent += 1

            except asyncio.TimeoutError:
                logger.warning(f'#{sent-1} message was timed-out.')
            except websockets.exceptions.ConnectionClosedOK:
                logger.warning('Websocket connection closed (ok).')
                break
            except websockets.exceptions.ConnectionClosedError:
                logger.warning('Websocket connection closed (error).')
                break
            except websockets.exceptions.ConnectionClosed:
                logger.warning('Websocket connection closed.')
                break
            except Exception:
                logger.exception("")
            finally:
                await asyncio.sleep(0.1)

    def send(self, message):
        """ Send message throught a websocket """
        with lock:
            self.overlay_messages.append(message)
