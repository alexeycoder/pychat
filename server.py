import asyncio
import socket
from socket import AF_INET

from common import *


def run_server(address: tuple[str, int]):
    log("Running server...")
    server = socket.create_server(address, family=AF_INET, reuse_port=True)
    server.listen()
    server.setblocking(False)
    log("Server listening at {}:{}".format(*address))

    # guest_connections: list[socket.socket] = []  # just fresh connection
    # list[tuple(socket.socket, str)] = []  # conn + username
    connections: dict[socket.socket, str] = dict()
    loop = asyncio.new_event_loop()
    loop.create_task(establish_connections(loop, server, connections))

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


async def establish_connections(loop: asyncio.AbstractEventLoop,
                                server: socket.socket,
                                connections: dict[socket.socket, str]):
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
        loop.create_task(handle_guest(loop, guest, connections))
        # loop.create_task(handle_client(loop, client, connections))


# async def finish_connections(loop: asyncio.AbstractEventLoop,
#                              connections: list[socket.socket]):
#     while connections:
#         conn = connections.pop()
#         with conn:
#             conn.shutdown(socket.SHUT_RDWR)


async def handle_guest(loop: asyncio.AbstractEventLoop,
                       guest: socket.socket,
                       connections: dict[socket.socket, str]):
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
                connections.update((guest, username,))
                loop.create_task(handle_client(loop, guest, connections))
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
                                 f"Still waiting for your username....")
                             )

    except asyncio.CancelledError:
        log(f"Cancelling a handle_guest task for {peername}.")
        await send_text(loop, guest,
                        "Connection closed due to server"
                        + " is shutting down. Bye!\n")
        await asyncio.sleep(0)
        guest.shutdown(socket.SHUT_RDWR)
        guest.close()
        raise
    finally:
        pass


def get_client_name(sender: socket.socket, recipient: socket.socket):
    if recipient is sender:
        return "Вы"
    return sender.getpeername()


async def handle_client(loop: asyncio.AbstractEventLoop,
                        client: socket.socket,
                        connections: dict[socket.socket, str]):
    with client:
        try:
            peername = client.getpeername()

            while True:
                await asyncio.sleep(0)
                data = await receive_chunk(loop, client)
                if not data:
                    log(f"Closed connection by {peername}.")
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                    break

                [await send_chunk(loop, conn, f"{get_client_name(client, conn)}:\n".encode(CHARSET) + data)
                 for conn in connections]

        except asyncio.CancelledError:
            await send_text(loop, client,
                            "Connection closed due to server"
                            + " is shutting down. Bye!\n")
            log(f"Cancelling a handle_client task for {peername}.")
            raise
        finally:
            if client in connections:
                connections.remove(client)


if __name__ == "__main__":
    run_server(LISTEN_ADDR)

# string to test:
# fgdnmblfmblfmnbfmnfklnmlkfmnkn fgknlmflkgnm f fnfklgn дылва вплщз пукщзп укзщпABC
