#!/usr/bin/env python3

import asyncio
import logging

log = logging.getLogger(__name__)
loop = None

def accept_client(client_reader, client_writer):

    log.info("New Connection")
    task = asyncio.Task(handle_client(client_reader, client_writer))

class EchoClient(asyncio.Protocol):

    #message = 'This is the message. It will be echoed.'
    writer = None
    transport = None

    def connection_made(self, transport):
        self.transport = transport
        print('connection made:', self)

    def data_received(self, data):
        self.writer.write(data)

    def eof_received(self):
        print("Got EOF from server connection")

    def connection_lost(self, exc):
        print("Got close from server connection")
        try:
            self.writer.write_eof()
        except Exception:
            pass

def conn_lost(tr):
    print("Got close from client connection")
    try:
        tr.write_eof()
    except Exception:
        pass


async def handle_client(client_reader, client_writer):
    data = None
    protocol = None

    try:
        data = await asyncio.wait_for(client_reader.read(1), timeout=1.0)
    except Exception:
        pass

    if data is None:
        log.info("opening ssh")

        try:
            _, protocol = await asyncio.ensure_future(loop.create_connection(EchoClient, "127.0.0.1", 8002)) # await asyncio.open_connection("127.0.0.1", 8002)
            protocol.writer = client_writer

            client_writer._protocol.other = protocol

        except Exception:
            pass

    else:
        log.info("opening vpn")

        try:
            _, protocol = await asyncio.ensure_future(loop.create_connection(EchoClient, "127.0.0.1", 8001)) # await asyncio.open_connection("127.0.0.1", 8001)
            protocol.writer = client_writer
            protocol.transport.write(data)

            client_writer._protocol.other = protocol
        except Exception:
            pass

    if protocol is None:
        print("Can't connect to the server")
        client_writer.write_eof()
        return

    client_writer._protocol.data_received = lambda data: protocol.transport.write(data)
    client_writer._protocol.eof_received = lambda : print("Got EOF from client connection")
    client_writer._protocol.connection_lost = lambda exc: conn_lost(protocol.transport)

def main():
    global loop
    loop = asyncio.get_event_loop()
    f = asyncio.start_server(accept_client, host=None, port=8000)
    loop.run_until_complete(f)
    loop.run_forever()

if __name__ == '__main__':
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # setup console logging
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)
    main()