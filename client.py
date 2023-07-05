import asyncio
import socket
from threading import Thread, current_thread

import controller
from common import *

loop = asyncio.new_event_loop()
conn: socket.socket = None
home_thread: Thread = None


def run_client(address: tuple[str, int], username: str):
    # для клиента вывод логов в консоль
    global home_thread
    home_thread = current_thread()
    global conn
    try:
        conn = socket.create_connection(address, timeout=10)
    except TimeoutError:
        controller.notify_no_connection()
        return

    conn.setblocking(False)

    loop.create_task(_receive_messages())
    loop.create_task(_say_hello_to_server(username))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print()
    finally:
        conn.shutdown(socket.SHUT_RDWR)
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.run_until_complete(asyncio.sleep(0))
        loop.close()
        print("Closing connection and exit...")
        pass


async def _say_hello_to_server(username):
    await send_chunk(loop, conn, hello_chunk_payload(username))
    # await loop.create_task(_send_random_messages())


async def _receive_messages():
    try:
        while True:
            await asyncio.sleep(0)
            data = await receive_chunk(loop, conn)
            if not data:
                print(f"Closed connection by server.")
                break

            username, content = get_message_from_chat_content(data)
            if not username:
                print("Received message of unexpected format:",
                      data.decode(CHARSET))
                continue

            print("Received message.")
            print("-"*80)
            print("User:", username)
            print("Message:", content)
            print("-"*80)
            controller.incoming(username, content)

    except asyncio.CancelledError:
        print(f"Cancelling receiving messages task.")
        await asyncio.sleep(0)
        raise
    finally:
        pass


# async def _send_random_messages():
#     cnt = 20
#     while cnt > 0:
#         cnt -= 1
#         n = random.randrange(8, 80)
#         s = str(cnt) + "-" + "".join(random.choices(
#             string.ascii_uppercase + string.ascii_lowercase + '\n', k=n))
#         await send_chunk(loop, conn, message_to_chat_chunk_payload(s))
#         print("-"*80)
#         print("_Sent:", s)
#         print("-"*80)
#         await asyncio.sleep(0)
#         await asyncio.sleep(10)
#     print('Sending complete!')


async def _send_message_async(text):
    print(f"Invoked message send async.")
    await send_chunk(loop, conn, message_to_chat_chunk_payload(text))
    await asyncio.sleep(0)


def send_message(text):
    if current_thread() is home_thread:
        loop.create_task(_send_message_async(text))
        return
    loop.call_soon_threadsafe(loop.create_task, _send_message_async(text))


def _stop_client():
    print(f"Invoked stop client async.")
    # for task in asyncio.all_tasks(loop):
    #     task.cancel()
    # # loop.run_until_complete(asyncio.sleep(0))
    loop.stop()


def stop_client():
    if current_thread() is home_thread:
        _stop_client()
        return
    loop.call_soon_threadsafe(_stop_client)

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
