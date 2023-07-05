import queue
import tkinter as tk

import controller


class ChatWindow:
    def __init__(self, username: str) -> None:
        self.username = username
        root = tk.Tk()
        root.title("ПайЧат, версия 1")

        label_username = tk.Label(root, text=username)
        label_username.grid(column=0, columnspan=2, row=0, sticky=tk.EW)

        messages_scroll = tk.Scrollbar(root)
        messages_text = tk.Text(root)  # , height=40, width=60)
        messages_text.configure(yscrollcommand=messages_scroll.set)
        messages_text.grid(column=0, row=1, sticky=tk.NSEW)
        messages_scroll.grid(column=1, row=1, sticky=tk.NS)
        messages_scroll.config(command=messages_text.yview)

        messages_text.tag_configure(
            'author', foreground='blue', justify='center', font='TkFixedFont', underline=True)
        messages_text.tag_configure(
            'message', border=1, borderwidth=1, font='TkFixedFont')

        entry_scroll = tk.Scrollbar(root)
        entry_text = tk.Text(root, height=6)
        entry_text.configure(yscrollcommand=entry_scroll.set)
        entry_text.grid(column=0, row=2, sticky=tk.NSEW)
        entry_scroll.grid(column=1, row=2, sticky=tk.NS)
        entry_scroll.config(command=entry_text.yview)

        button_send = tk.Button(root, text="Отправить (Alt+Enter)",
                                command=controller.send)
        button_send.grid(column=0, columnspan=2, row=3, sticky=tk.EW)

        root.bind('<Alt-Return>', lambda event=None: controller.send())
        root.bind('<Alt-KP_Enter>', lambda event=None: controller.send())
        root.bind('<<NewMessage>>', self.__add_message)
        root.protocol('WM_DELETE_WINDOW', self.__dispose)

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)

        root.grid_rowconfigure(0, weight=0)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=0)
        root.grid_rowconfigure(3, weight=0)

        ChatWindow.center_to_screen(root)
        self.message_text = messages_text
        self.entry_text = entry_text
        self.root = root

        self.messages_queue = queue.LifoQueue[tuple[str, str]]()

    def run(self):
        self.root.mainloop()

    def pop_text(self):
        text = self.entry_text.get('1.0', tk.END)
        self.entry_text.delete('1.0', tk.END)
        return text

    def add_message_threadsafe(self, username, text):
        self.messages_queue.put((username, text,))
        print("add_message_threadsafe username =", username)
        print("add_message_threadsafe text =", text)
        self.root.event_generate('<<NewMessage>>', when='tail')

    def __add_message(self, event):
        while not self.messages_queue.empty():
            item = self.messages_queue.get()
            if not item:
                return

            username, text = item
            print("username", username)
            print("text", text)
            self.message_text.insert(tk.END, "\n\n"+username, 'author')
            self.message_text.insert(tk.END, "\n"+text, 'message')
            self.message_text.see(tk.END)

    def __dispose(self):
        controller.handle_window_close()
        self.root.destroy()

    @staticmethod
    def center_to_screen(window: tk.Toplevel):
        MIN_SHIFT = 1
        window.update_idletasks()
        s_width, s_height = window.winfo_screenwidth(), window.winfo_screenheight()
        w_width, w_height = window.winfo_width(), window.winfo_height()
        dx, dy = max(MIN_SHIFT, (s_width-w_width)//2), \
            max(MIN_SHIFT, (s_height-w_height)//2)
        window.geometry(f'+{dx}+{dy}')
