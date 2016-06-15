#!/usr/bin/env python3
"""TCP relay based on 1-second wait (2 states)."""

import asyncio
import logging
import argparse

import sys
try:
    import signal
except ImportError:
    signal = None


log = logging.getLogger(__name__)
loop = None

RELAY_WAIT_PORT = 8001
RELAY_ACTION_PORT = 8002


class ServerRetranslator(asyncio.Protocol):
    """Handler for server"""

    writer = None
    transport = None

    def connection_made(self, transport):
        self.transport = transport
        log.info('Connection made: {0}'.format(self))

    def data_received(self, data):
        self.writer.write(data)

    def eof_received(self):
        log.info("Got EOF from server")

    def connection_lost(self, exc):
        log.info("Got close from server")
        try:
            self.writer.write_eof()
        except Exception:
            pass


def accept_client(client_reader, client_writer):
    log.info("New Connection")
    task = asyncio.Task(handle_client(client_reader, client_writer))


async def handle_client(client_reader, client_writer):
    data = None
    port = None
    protocol = None
    client_protocol = client_writer._protocol

    try:
        data = await asyncio.wait_for(client_reader.read(1), timeout=1.0)
    except Exception:
        pass

    if data is None:
        log.info("opening RELAY_WAIT_PORT")
        port = RELAY_WAIT_PORT
    else:
        log.info("opening RELAY_ACTION_PORT")
        port = RELAY_ACTION_PORT

    try:
        _, protocol = await asyncio.ensure_future(
            loop.create_connection(ServerRetranslator, "127.0.0.1", port))

        protocol.writer = client_writer
        client_protocol.other = protocol

        if data is not None:
            protocol.transport.write(data)

    except Exception:
        pass

    if protocol is None:
        log.error("Can't connect to the server")
        client_writer.write_eof()
        return

    def conn_lost(tr):
        log.info("Got close from client")
        try:
            tr.write_eof()
        except Exception:
            pass

    client_protocol.data_received = lambda data: protocol.transport.write(data)
    client_protocol.eof_received = lambda: log.info("Got EOF from client")
    client_protocol.connection_lost = lambda exc: conn_lost(protocol.transport)


ARGS = argparse.ArgumentParser(description="TCP relay.")

ARGS.add_argument(
    '--port', action="store", dest='port',
    default=8000, type=int, help='Output port')

ARGS.add_argument(
    '--waiter', action="store", dest='wait_port',
    default=8001, help='Port of waiter protocol')

ARGS.add_argument(
    '--actioner', action="store", dest='action_port',
    default=8002, help='Port of actioner protocol')


if __name__ == '__main__':
    args = ARGS.parse_args()

    RELAY_ACTION_PORT = args.action_port
    RELAY_WAIT_PORT = args.wait_port


    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # setup console logging
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    # start the server

    loop = asyncio.get_event_loop()

    if signal is not None and sys.platform != 'win32':
        loop.add_signal_handler(signal.SIGINT, loop.stop)

    f = asyncio.start_server(accept_client, host=None, port=args.port)
    loop.run_until_complete(f)
    loop.run_forever()
