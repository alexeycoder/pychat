from functools import partial
import tkinter as tk
from tkinter import ttk
import controller


class ChatWindow:
    def __init__(self, username: str) -> None:
        self.username = username
        root = tk.Tk()
        root.title("ПайЧат, версия 1")

        messages_scroll = tk.Scrollbar(root)
        messages_text = tk.Text(root)  # , height=40, width=60)
        messages_text.configure(yscrollcommand=messages_scroll.set)
        messages_text.grid(column=0, row=0, sticky=tk.NSEW)
        messages_scroll.grid(column=1, row=0, sticky=tk.NS)
        messages_scroll.config(command=messages_text.yview)

        entry_scroll = tk.Scrollbar(root)
        entry_text = tk.Text(root, height=6)
        entry_text.configure(yscrollcommand=entry_scroll.set)
        entry_text.grid(column=0, row=1, sticky=tk.NSEW)
        entry_scroll.grid(column=1, row=1, sticky=tk.NS)
        entry_scroll.config(command=entry_text.yview)

        insert_text = """GEEKSFORGEEKS :
        A Computer Science portal for geeks.
        It contains well written, well thought
        and well explained computer science and
        programming articles, quizzes and
        many more.
        GeeksforGeeks realises the importance of programming practice in the field of
        Computer Science.
        That is why, it also provides an option of practicing problems.
        This huge database of problems is created by programming experts.
        The active team of GeeksforGeeks makes the learning process
        interesting and fun.
        """
        messages_text.insert(tk.END, insert_text)

        button_send = tk.Button(root, text="Отправить (Alt+Enter)",
                                command=controller.send)
        button_send.grid(column=0, row=2, sticky=tk.EW)
        root.bind('<Alt-Return>', lambda event=None: controller.send())
        root.bind('<Alt-KP_Enter>', lambda event=None: controller.send())

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=0)

        ChatWindow.center_to_screen(root)
        self.entry_text = entry_text
        self.root = root

    def run(self):

        self.root.mainloop()

    def pop_text(self):
        text = self.entry_text.get('1.0', 'end')
        self.entry_text.delete('1.0', 'end')
        return text

    def add_message(self, username, text):
        ...

    @staticmethod
    def center_to_screen(window: tk.Toplevel):
        MIN_SHIFT = 1
        window.update_idletasks()
        s_width, s_height = window.winfo_screenwidth(), window.winfo_screenheight()
        w_width, w_height = window.winfo_width(), window.winfo_height()
        dx, dy = max(MIN_SHIFT, (s_width-w_width)//2), \
            max(MIN_SHIFT, (s_height-w_height)//2)
        window.geometry(f'+{dx}+{dy}')
