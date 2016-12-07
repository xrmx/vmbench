from tornado.ioloop import IOLoop
from tornado.platform.asyncio import BaseAsyncIOLoop
from tornado.tcpserver import TCPServer

import argparse
import uvloop


class AsyncIOUvloop(BaseAsyncIOLoop):
    def initialize(self, **kwargs):
        loop = uvloop.new_event_loop()
        try:
            super(BaseAsyncIOLoop, self).initialize(loop, close_loop=True, **kwargs)
        except Exception:
            # If initialize() does not succeed (taking ownership of the loop),
            # we have to close it.
            loop.close()
            raise


class StreamHandler:
    def __init__(self, stream):
        self._stream = stream
        stream.set_nodelay(True)
        self._stream.read_until(b'\n', self._handle_read)

    def _handle_read(self, data):
        self._stream.write(data)
        self._stream.read_until(b'\n', self._handle_read)


class EchoServer(TCPServer):
    def handle_stream(self, stream, address):
        StreamHandler(stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--uvloop', default=False, action='store_true')
    args = parser.parse_args()

    if args.uvloop:
        print('using UVLoop')
        IOLoop.configure(AsyncIOUvloop)
    else:
        IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
        print('using asyncio loop')

    server = EchoServer()
    server.bind(25000)
    server.start(1)
    IOLoop.instance().start()
    IOLoop.instance().close()
