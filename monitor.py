from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
# from dialog_edit import Dialog


class Table(object):

    def __init__(self):
        # super(Table, self).__init__()
        self.tree = None
        self.servers = [
            ("DC", "OK" ),
            ("DC2", "OK" ),
            ("DC3", "OK" ),
            ("DCStore", "OK" ),
            ("DCStore1", "OK" ),
            ("HVStore", "OK" ),
            ("DBS", "OK" ),
            ("SQLServ", "OK"),
            ("SQLServ2", "OK"),
            ("Appserv", "OK"),
            ("WDS", "OK"),
            ("TSS", "OK"),
            ("TSS2", "OK"),
            ("RDS2", "OK"),
            ("mail.alpha-medica.ru", "OK"),
            ("sec.it-ra.ru", "OK"),
            ("VMMS", "OK"),
            ("83.222.197.218", "OK"),
            ("83.222.197.221", "OK")
        ]


        self.setup_ui()
        self.add_all_servers()


    def setup_ui(self):

        container = ttk.Frame()
        # container.pack(fill='both', expand=True)
        container.pack(fill='x', side=TOP, pady=10, padx=5, expand=False)

        # self.tree = ttk.Treeview(columns=("columns1","columns2" ), show="headings", selectmode="browse")
        self.tree = ttk.Treeview(container, columns=("columns1","columns2" ), show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.heading("#1", text="Сервер")
        self.tree.heading("#2", text="Состояние")
        self.tree.bind("<<TreeviewSelect>>", self.select)
        self.tree.pack()

        padx_button = 25
        container2 = ttk.Frame()
        container2.pack(fill='x', side=TOP, pady=10, padx=10)
        button_exit = Button(container2, text="Изменить", width=15, command=self.edit_server)
        button_exit.pack(side=LEFT, padx=(0,padx_button))
        button_add = Button(container2, text="Добавить", width=15, command=self.add_server)
        button_add.pack(side=LEFT, padx=(0,padx_button))
        button_del = Button(container2, text="Удалить", width=15, command=self.remove_server)
        button_del.pack(side=LEFT, padx=(0,padx_button))

        container_interval = ttk.Frame()
        container_interval.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_interval = Label(container_interval, text="Интервал")
        label_interval.pack( side=LEFT, padx=5)
        entry_interval = Entry(container_interval, width=10)
        entry_interval.pack( side=RIGHT, padx=(0, 200))

        container_numcheck = ttk.Frame()
        container_numcheck.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_numcheck = Label(container_numcheck, text="Количество проверок")
        label_numcheck.pack( side=LEFT,padx=5)
        entry_numcheck = Entry(container_numcheck, width=10)
        entry_numcheck.pack( side=RIGHT, padx=(0, 200))

        container_email = ttk.Frame()
        container_email.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_email = Label(container_email, text="E-Mail")
        label_email.pack( side=LEFT,padx=5)
        entry_email = Entry(container_email, width=50)
        entry_email.pack( side=RIGHT, padx=(0, 0))



        container3 = ttk.Frame()
        container3.pack(fill='x', side=TOP, pady=10, padx=10)
        button_exit = Button(container3, text="Выйти", width=15, command=root.quit)
        button_exit.pack(side=RIGHT, padx=(0, padx_button))
        button_save = Button(container3, text="Сохранить", width=15, command=self.add_server)
        button_save.pack(side=RIGHT, padx=(0, padx_button))
        button_del = Button(container3, text="Отмена", width=15)
        button_del.pack(side=RIGHT, padx=(0, padx_button))

    def select(self, event):
        print(self.tree.selection())

        for nm in self.tree.selection():
            server, state = self.tree.item(nm, 'values')
            print(server)
            print(state)

    def add_all_servers(self):
        for values in self.servers:
            self.tree.insert("", END, values=values)

    def add_server(self):
        server_name = simpledialog.askstring("Добавить сервер", "Имя сервера")

        if server_name is not None:
            self.tree.insert("", END, values=(server_name, "OK"))
        # print(server_name)

    def edit_server(self):
        server, state = ('', '')
        for nm in self.tree.selection():
            server, state = self.tree.item(nm, 'values')
        if server:
            self.create_toplevel(server, state)
        else:
            print("Выберите сервер")


    def remove_server(self):
        self.tree.delete(self.tree.selection())

    def create_toplevel(self, server, state):

        self.toplevel_dialog = Toplevel(root)
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

if __name__ == '__main__':
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    table = Table()
    root.mainloop()