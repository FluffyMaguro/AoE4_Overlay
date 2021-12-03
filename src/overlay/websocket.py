import asyncio
import json
import threading
import traceback

import websockets
from websockets.legacy.server import serve as websockets_serve

lock = threading.Lock()


class Websocket_connection_manager():
    """ Class managing connection through a websocket to the HTML file"""
    def __init__(self, port=7307):
        self.overlay_messages = []
        self.port = port

    def run(self):
        self.thread_server = threading.Thread(target=self.start_manager,
                                              daemon=True)
        self.thread_server.start()

    def start_manager(self):
        try:
            print('Starting a websocket server')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            start_server = websockets_serve(self.manager, 'localhost',
                                            self.port)
            loop.run_until_complete(start_server)
            loop.run_forever()
        except Exception:
            traceback.print_exc()

    @staticmethod
    async def _send_ws_message(websocket, message):
        message = json.dumps(message)
        print(f"WS sending: {message}")
        await asyncio.wait_for(asyncio.gather(websocket.send(message)),
                               timeout=1)

    async def manager(self, websocket, path):
        """ Manages websocket connection for each client """
        print(f"Opening: {websocket}")

        # Send the last message if there is one
        if len(self.overlay_messages) > 0:
            await self._send_ws_message(websocket, self.overlay_messages[-1])

        sent = len(self.overlay_messages)

        while True:
            try:
                if len(self.overlay_messages) == sent:
                    continue

                await self._send_ws_message(websocket,
                                            self.overlay_messages[sent])
                sent += 1

            except asyncio.TimeoutError:
                print(f'#{sent-1} message was timed-out.')

            except websockets.exceptions.ConnectionClosedOK:
                print('Websocket connection closed (ok).')
                break

            except websockets.exceptions.ConnectionClosedError:
                print('Websocket connection closed (error).')
                break

            except websockets.exceptions.ConnectionClosed:
                print('Websocket connection closed.')
                break

            except Exception:
                traceback.print_exc()

            finally:
                await asyncio.sleep(0.1)

    def send(self, event):
        """ Send message throught a websocket """
        with lock:
            self.overlay_messages.append(event)
