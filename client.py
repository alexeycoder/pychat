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
        loop.create_task(say_hello_to_server(loop, conn))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            conn.shutdown(socket.SHUT_RDWR)


async def say_hello_to_server(loop: asyncio.AbstractEventLoop,
                              conn: socket.socket):
    await send_chunk(loop, conn, hello_chunk_payload("Алексей" + str(random.randint(1000, 9999))))
    await loop.create_task(send_random_messages(loop, conn))


async def receive_messages(loop: asyncio.AbstractEventLoop,
                           conn: socket.socket):
    while True:
        await asyncio.sleep(0)
        data = await receive_chunk(loop, conn)
        if not data:
            log(f"Closed connection by server.")
            break

        username, content = get_message_from_chat_content(data)
        if not username:
            log("Received message of unexpected format:", data.decode(CHARSET))
            continue

        print("-"*80)
        print("User:", username)
        print("Message:", content)
        print("-"*80)


async def send_random_messages(loop: asyncio.AbstractEventLoop,
                               conn: socket.socket):
    cnt = 20
    while cnt > 0:
        cnt -= 1
        n = random.randrange(8, 80)
        s = str(cnt) + "-" + "".join(random.choices(
            string.ascii_uppercase + string.ascii_lowercase + '\n', k=n))

        await send_chunk(loop, conn, message_to_chat_chunk_payload(s))
        print("-"*80)
        print("_Sent:", s)
        print("-"*80)
        await asyncio.sleep(0)
        await asyncio.sleep(10)

    print('Sending complete!')


if __name__ == "__main__":
    run_client(SERVER_ADDR)
