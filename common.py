import asyncio
import socket
import json

PORT = 12345
LISTEN_ADDR = ("", PORT,)
SERVER_ADDR = ("localhost", PORT,)
SERVER_NAME = "Chat Server"
CHARSET = "utf-8"
BUF_SIZE = 4096
LEN_PREFIX_DELIMITER = b":"


def log(msg):
    print("log:", msg)


async def send_chunk(loop: asyncio.AbstractEventLoop,
                     conn: socket.socket,
                     payload: bytes):
    final_msg = bytearray(f"{len(payload)}:", CHARSET)
    final_msg.extend(payload)
    await asyncio.sleep(0)
    return await loop.sock_sendall(conn, final_msg)


async def send_text(loop: asyncio.AbstractEventLoop,
                    conn: socket.socket,
                    text: str):
    return await send_chunk(loop, conn, text.encode(CHARSET))


async def __receive_prefix(loop: asyncio.AbstractEventLoop,
                           conn: socket.socket):
    # try:
    prefix = bytearray()
    while True:
        portion = await loop.sock_recv(conn, 1)
        if not portion:
            return None
        if portion == LEN_PREFIX_DELIMITER:
            break
        prefix.extend(portion)
        if portion not in b"0123456789":
            return (False, prefix)

    prefix_value = int(prefix)
    log(f"Detected prefixed message (prefix={prefix_value}).")
    return (True, prefix_value)
    # except:
    #     return None


async def receive_chunk(loop: asyncio.AbstractEventLoop,
                        conn: socket.socket):
    prefix_tuple = await __receive_prefix(loop, conn)
    if prefix_tuple is None:
        return None

    is_len, prefix = prefix_tuple
    if not is_len:
        raw = await loop.sock_recv(conn, BUF_SIZE)
        prefix.extend(raw)
        return bytes(prefix)

    chunk_len = int(prefix)
    chunk = bytearray()
    while len(chunk) < chunk_len:
        portion = await loop.sock_recv(conn, chunk_len - len(chunk))
        if not portion:
            return None
        chunk.extend(portion)
    return bytes(chunk)


def json_dumps(d: dict):
    return json.dumps(d, separators=(',', ':'))


# hello

def hello_chunk_payload(username: str) -> bytes:
    d = {"type": "hello",
         "username": username}
    s = json_dumps(d)
    return s.encode(CHARSET)


def get_hello_username(payload: bytes) -> str:
    s = payload.decode(CHARSET)
    d: dict = json.loads(s)
    assert "type" in d and d["type"] == "hello"
    return d.get("username", None)


# message to chat

def message_to_chat_chunk_payload(content) -> bytes:
    d = {"type": "text",
         "content": content}
    s = json_dumps(d)
    return s.encode(CHARSET)


def get_message_to_chat_content(payload: bytes) -> str:
    s = payload.decode(CHARSET)
    d: dict = json.loads(s)
    assert "type" in d and d["type"] == "text"
    return d.get("content", "")


# message from chat

def message_from_chat_chunk_payload(username, content) -> bytes:
    d = {"type": "message",
         "username": username,
         "content": content}
    s = json_dumps(d)
    return s.encode(CHARSET)


def get_message_to_chat_content(payload: bytes) -> tuple[str, str]:
    s = payload.decode(CHARSET)
    d: dict = json.loads(s)
    assert "type" in d and d["type"] == "message"
    return d.get("username", "Unknown"), d.get("content", "")
