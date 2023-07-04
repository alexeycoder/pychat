from functools import partial
from threading import Thread
from chat_window import ChatWindow
import client

window: ChatWindow
client_thread: Thread

def run():
    # global client_thread
    # from common import SERVER_ADDR
    # client_thread = Thread(target=partial(client.run_client, SERVER_ADDR))
    # client_thread.start()

    run_window()


def run_window():
    global window
    window = ChatWindow("UserName")
    window.run()


def send():
    text = window.pop_text()
    client.send_message(text)


def incoming(username, text):
    ...
