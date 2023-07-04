from functools import partial
import random
import socket
import asyncio
import string
from threading import Thread, current_thread
from common import *

loop = asyncio.new_event_loop()
conn: socket.socket
home_thread: Thread


def run_client(address: tuple[str, int]):
    # global loop
    # loop = asyncio.new_event_loop()
    global home_thread
    home_thread = current_thread().ident
    global conn
    with socket.create_connection(address) as conn:
        conn.setblocking(False)

        loop.create_task(_receive_messages())
        loop.create_task(_say_hello_to_server())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            conn.shutdown(socket.SHUT_RDWR)


async def _say_hello_to_server():
    await send_chunk(loop, conn, hello_chunk_payload("Алексей" + str(random.randint(1000, 9999))))
    # await loop.create_task(_send_random_messages())


async def _receive_messages():
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


async def _send_random_messages():
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


async def _send_message_async(text):
    log(f"_invoked async sending: {text}")
    n = random.randrange(8, 80)
    s = text + "\n" + "".join(random.choices(
        string.ascii_uppercase + string.ascii_lowercase, k=n))

    await send_chunk(loop, conn, message_to_chat_chunk_payload(s))
    print("-"*80)
    print("_Sent:", s)
    print("-"*80)
    await asyncio.sleep(0)


def send_message(text):
    if current_thread() is home_thread:
        loop.create_task(_send_message_async(text))
        return
    loop.call_soon_threadsafe(loop.create_task, _send_message_async(text))

    # def _add_task(func, fut: asyncio.Future):
    #     try:
    #         ret = func()
    #         fut.set_result(ret)
    #     except Exception as e:
    #         fut.set_exception(e)

    # log(f"_sending: {text}")

    # fu = asyncio.Future()
    # loop.call_soon_threadsafe(
    #     _add_task,
    #     partial(send_chunk, loop, conn, message_to_chat_chunk_payload(text)),
    #     fu)

    # log(f"_sending task created: {text}")


# if __name__ == "__main__":
#     run_client(SERVER_ADDR)
