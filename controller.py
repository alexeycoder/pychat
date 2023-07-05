import re
from functools import partial
from threading import Thread
from tkinter import simpledialog, messagebox

import client
from chat_window import ChatWindow

IP_REGEX = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]):\d{1,5}$"
# IP_REGEX = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

window: ChatWindow = None
client_thread: Thread = None


def send():
    text = window.pop_text()
    if text.strip():
        client.send_message(text)


def incoming(username, text):
    global window
    if window:
        window.add_message_threadsafe(username, text)


def handle_window_close():
    client.stop_client()
    client_thread.join()


def notify_no_connection():
    client.stop_client()
    messagebox.showerror("Ошибка",
                         "Не удалось установить соединение: сервер не отвечает.")


def _ask_username():
    while True:
        answer = simpledialog.askstring(
            "Ваше имя",
            "Для входя в чат требуется ваше имя.\nПожалуйста представьтесь:",
            initialvalue=""
        )
        if answer is None:
            exit()
        elif answer:
            return answer


def _ask_address():
    err = False
    while True:
        prompt = ("Введите IP-адрес и номер порта сервера чата\n"
                  "в формате XXX.XXX.XXX.XXX:ПОРТ")
        if err:
            err = False
            prompt = "Некорректный ввод! Попробуйте ещё раз.\n" + prompt
        answer = simpledialog.askstring(
            "Адрес чата",
            prompt,
            initialvalue="194.67.74.161:12345"
        )
        if answer is None:
            exit()

        answer = answer.strip()
        if answer and re.match(IP_REGEX, answer):
            host, port_str = answer.split(":")
            port = int(port_str)
            if 0 < port < 2**16:
                return (host, port)
        err = True


def run():
    global window
    username = _ask_username()
    window = ChatWindow(username)
    addr = _ask_address()

    global client_thread
    client_thread = Thread(target=partial(client.run_client, addr, username))
    client_thread.start()

    window.run()
