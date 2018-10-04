from tkinter import *
from tkinter import ttk

class Dialog(Toplevel):
    def __init__(self, server="", state=""):
        self.toplevel_dialog = Toplevel()
        self.toplevel_dialog.minsize(300, 100)
        self.toplevel_dialog.protocol("WM_DELETE_WINDOW", self.close_toplevel)

        container_server = ttk.Frame(self.toplevel_dialog)
        container_server.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.toplevel_dialog_label = ttk.Label(container_server, text='Сервер')
        self.toplevel_dialog_label.pack(side=LEFT)
        self.toplevel_entry_server = Entry(container_server, width=30)
        self.toplevel_entry_server.insert(0, server)
        self.toplevel_entry_server.pack(side=RIGHT)

        container_state = ttk.Frame(self.toplevel_dialog)
        container_state.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.toplevel_dialog_label = ttk.Label(container_state, text='Состояние')
        self.toplevel_dialog_label.pack(side=LEFT)
        self.toplevel_entry_state = Entry(container_state, width=30)
        self.toplevel_entry_state.insert(0,state)
        self.toplevel_entry_state.pack(side=RIGHT)

        container_buttons = ttk.Frame(self.toplevel_dialog)
        container_buttons.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.toplevel_dialog_yes_button = ttk.Button(container_buttons, text='Сохранить')
        self.toplevel_dialog_yes_button.pack(side=LEFT, fill='x', expand=True)
        self.toplevel_dialog_no_button = ttk.Button(container_buttons, text='Отмена', command=self.close_toplevel)
        self.toplevel_dialog_no_button.pack(side=LEFT, fill='x', expand=True)

    def close_toplevel(self):
        self.toplevel_dialog.destroy()


# if __name__ == '__main__':
#     root = Tk()
#     root.resizable(width=FALSE, height=FALSE)
#     top = Dialog()
#     root.mainloop()
