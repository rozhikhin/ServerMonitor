from tkinter import *
from tkinter import ttk

class Dialog(Frame, object):
    def __init__(self, master, server="", state="", edit=False):
        Frame.__init__(self, master)
        self.master = master
        # self.edit = edit
        self.toplevel_dialog = Toplevel()
        self.toplevel_dialog.minsize(300, 100)
        self.toplevel_dialog.protocol("WM_DELETE_WINDOW", self.close_toplevel)
        self.toplevel_dialog.transient(master)

        if edit:
            self.toplevel_dialog.title("Редактировать запись")
        else:
            self.toplevel_dialog.title("Добавить запись")

        self.toplevel_dialog.grab_set()
        self.toplevel_dialog.focus_set()

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
        self.toplevel_dialog_yes_button = ttk.Button(container_buttons, text='Сохранить', command=self.get_text)
        self.toplevel_dialog_yes_button.pack(side=LEFT, fill='x', expand=True)
        self.toplevel_dialog_no_button = ttk.Button(container_buttons, text='Отмена', command=self.close_toplevel)
        self.toplevel_dialog_no_button.pack(side=LEFT, fill='x', expand=True)

    def get_text(self):
        server_name = self.toplevel_entry_server.get()
        state = self.toplevel_entry_state.get()
        self.master.save_server({"server_name": server_name, "state": state})
        self.close_toplevel()


    def close_toplevel(self):
        self.toplevel_dialog.destroy()


