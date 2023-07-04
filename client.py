import random
import socket
from socket import SOCK_STREAM
import asyncio
import string
import time
from common import *


def run_client(address):
    with socket.create_connection(address) as conn:
        conn.setblocking(False)
        loop = asyncio.new_event_loop()
        loop.create_task(receive_messages(loop, conn))
        loop.create_task(send_random_messages(loop, conn))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            conn.shutdown(socket.SHUT_RDWR)


async def receive_messages(loop: asyncio.AbstractEventLoop,
                           conn: socket.socket):
    while True:
        data = await receive_chunk(loop, conn)
        if not data:
            log(f"Closed connection by server.")
            break

        msg = data.decode(CHARSET)
        print("-"*80)
        print("Received:", msg)
        print("-"*80)
        await asyncio.sleep(0)


async def send_random_messages(loop: asyncio.AbstractEventLoop,
                               conn: socket.socket):
    cnt = 20
    while cnt > 0:
        cnt -= 1
        n = random.randrange(8, 80)
        s = ''.join(random.choices(
            string.ascii_uppercase + string.ascii_lowercase + '\n', k=n))
        # sb = (s + "\n").encode(CHARSET)
        # sb = str(len(sb)).encode(CHARSET) + LEN_PREFIX_DELIMITER + sb

        await send_text(loop, conn, s + "\n")
        print("-"*80)
        print("_Sent:", s)
        print("-"*80)
        # response = await receive_chunk(loop, conn)
        # print("_Received: ", response.decode(CHARSET))
        await asyncio.sleep(0)
        time.sleep(1)

    print('Sending complete!')


if __name__ == "__main__":
    run_client(SERVER_ADDR)
