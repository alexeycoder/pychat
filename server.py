import asyncio
import socket
from socket import AF_INET

from common import *

loop = asyncio.new_event_loop()
connections = dict[socket.socket, str]() # { sock : username }
server: socket.socket


def run_server(address: tuple[str, int]):
    log("Running server...")
    global server
    server = socket.create_server(address, family=AF_INET, reuse_port=True)
    server.listen()
    server.setblocking(False)
    log("Server listening at {}:{}".format(*address))

    loop.create_task(establish_connections())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print()
        server.shutdown(socket.SHUT_RDWR)
        server.close()
        for task in asyncio.all_tasks(loop):
            task.cancel()
        # loop.run_until_complete(finish_connections(loop, connections))
        loop.run_until_complete(asyncio.sleep(0))
        loop.close()
        log("Closing all connections and exit...")


async def establish_connections():
    while True:
        await asyncio.sleep(0)
        guest, addr = await loop.sock_accept(server)
        await send_chunk(loop, guest,
                         message_from_chat_chunk_payload(
                             SERVER_NAME,
                             "Connection established. Waiting for your username...")
                         )
        # connections.append(client)
        log(
            f"Established connection from {addr}. Waiting for hello message with username...")
        loop.create_task(handle_guest(guest))
        # loop.create_task(handle_client(loop, client, connections))


# async def finish_connections(loop: asyncio.AbstractEventLoop,
#                              connections: list[socket.socket]):
#     while connections:
#         conn = connections.pop()
#         with conn:
#             conn.shutdown(socket.SHUT_RDWR)


async def handle_guest(guest: socket.socket):
    try:
        peername = guest.getpeername()

        while True:
            await asyncio.sleep(0)
            data = await receive_chunk(loop, guest)
            if not data:
                log(f"Closed connection by {peername}.")
                guest.shutdown(socket.SHUT_RDWR)
                guest.close()
                break

            # если получено hello-message с username -- переводим в чат
            username = get_hello_username(data)
            if username:
                connections[guest] = username
                loop.create_task(handle_client(guest))
                log(f"User {username}@{peername} has been registered.")
                await send_chunk(loop, guest,
                                 message_from_chat_chunk_payload(
                                     SERVER_NAME,
                                     f"Welcome, {username}.")
                                 )
                break

            # получено что-то, но не hello-message -- продолжаем ждать hello
            await send_chunk(loop, guest,
                             message_from_chat_chunk_payload(
                                 SERVER_NAME,
                                 "Still waiting for your username....")
                             )

    except asyncio.CancelledError:
        log(f"Cancelling handle_guest task for {peername}.")
        await send_chunk(loop, guest,
                         message_from_chat_chunk_payload(
                             SERVER_NAME,
                             "Connection closed due to server"
                             + " is shutting down. Bye!\n"))
        await asyncio.sleep(0)
        guest.shutdown(socket.SHUT_RDWR)
        guest.close()
        raise
    finally:
        pass


async def handle_client(client: socket.socket):
    with client:
        try:
            peername = client.getpeername()

            while True:
                await asyncio.sleep(0)
                data = await receive_chunk(loop, client)
                if not data:
                    break

                assert client in connections
                username = connections[client]

                message_content = get_message_to_chat_content(data)
                if message_content is None:
                    log(
                        f"A message of unexpected format received from {username}, {peername}.")
                    await asyncio.sleep(0)
                    continue

                # эхо сообщение себе:
                await send_chunk(loop, client, message_from_chat_chunk_payload(SELF_NAME, message_content))
                # остальным участникам:
                [await send_chunk(loop, conn, message_from_chat_chunk_payload(uname, message_content))
                 for conn, uname in connections.items() if conn is not client]

            # участник закрыл соединение
            log(f"Closed connection by {peername}.")
            if client in connections:
                connections.pop(client)
            [await send_chunk(loop, conn, message_from_chat_chunk_payload(SERVER_NAME, f"{username} покинул чат."))
             for conn, uname in connections.items()]
            client.shutdown(socket.SHUT_RDWR)
            client.close()

        except asyncio.CancelledError:
            log(f"Cancelling handle_client task for {peername}.")
            await send_chunk(loop, client,
                             message_from_chat_chunk_payload(
                                 SERVER_NAME,
                                 "Connection closed due to server"
                                 + " is shutting down. Bye!\n"))
            await asyncio.sleep(0)
            raise
        finally:
            if client in connections:
                connections.pop(client)


if __name__ == "__main__":
    run_server(LISTEN_ADDR)

# string to test:
# fgdnmblfmblfmnbfmnfklnmlkfmnkn fgknlmflkgnm f fnfklgn дылва вплщз пукщзп укзщпABC
