from tkinter import *
from tkinter import ttk
from dialog import Dialog
from tkinter import messagebox
from sqlapi import DB

class Table(Frame, object):
    def __init__(self, master):
        Frame.__init__(self)
        # Инициализация перменных
        # Таблица со списком серверов
        self.tree = None
        # Дочернее окно для редактирования и добавления записей
        # self.dialog = None
        # Данные, приходящие из дочернего окна
        self.toplevel_data = None
        # Редактируется ли запись (self.edit = True) или создается новая (self.edit = False)
        self.edit = False
        self.servers = list()
        self.sqlapi = DB()
        self.sqlapi.init_db()

        self.servers.sort()

        self.setup_ui()
        self.add_all_servers()
        self.get_settings()


    def setup_ui(self):

        container = ttk.Frame()
        # container.pack(fill='both', expand=True)
        container.pack(fill='x', side=TOP, pady=10, padx=5, expand=False)

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
        self.entry_interval = Entry(container_interval, width=10)
        self.entry_interval.pack( side=RIGHT, padx=(0, 200))

        container_numcheck = ttk.Frame()
        container_numcheck.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_numcheck = Label(container_numcheck, text="Количество проверок")
        label_numcheck.pack( side=LEFT,padx=5)
        self.entry_numcheck = Entry(container_numcheck, width=10)
        self.entry_numcheck.pack( side=RIGHT, padx=(0, 200))

        container_email = ttk.Frame()
        container_email.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_email = Label(container_email, text="E-Mail")
        label_email.pack( side=LEFT,padx=5)
        self.entry_email = Entry(container_email, width=50)
        self.entry_email.pack( side=RIGHT, padx=(0, 0))



        container3 = ttk.Frame()
        container3.pack(fill='x', side=TOP, pady=10, padx=10)
        button_exit = Button(container3, text="Выйти", width=15, command=root.quit)
        button_exit.pack(side=RIGHT, padx=(0, padx_button))
        button_save = Button(container3, text="Сохранить", width=15, command=self.save_settings)
        button_save.pack(side=RIGHT, padx=(0, padx_button))
        button_del = Button(container3, text="Отмена", width=15)
        button_del.pack(side=RIGHT, padx=(0, padx_button))

    def select(self, event=None):
        for nm in self.tree.selection():
            server_name, state = self.tree.item(nm, 'values')
        return {'server_name': server_name, 'state': state}

    def add_all_servers(self):
        self.servers = self.sqlapi.get_servers()
        if self.servers is not None:
            for values in self.servers:
                self.tree.insert("", END, values=values)

    def add_server(self):
        self.edit = False
        self.create_toplevel()

    def save_server(self, data):
        if self.edit:
            self.tree.delete(self.tree.selection())
        self.tree.insert("", END, values=(data["server_name"], data["state"]))
        self.sqlapi.save_server(data)

        servers = []
        for item in self.tree.get_children():
            server, state = self.tree.item(item, 'values')
            servers.append((server, state))
            servers.sort()
        self.tree.delete(*self.tree.get_children())
        for values in servers:
            self.tree.insert("", END, values=values)

    def edit_server(self):
        self.edit = True
        server, state = ('', '')
        for nm in self.tree.selection():
            server, state = self.tree.item(nm, 'values')
        if server:
            self.create_toplevel(server, state)
        else:
            messagebox.showinfo("Выберите сервер", "Необходимо выбрать сервер для редактирования")

    def remove_server(self):
        # self.tree.delete(*self.tree.get_children())
        select_server = self.select()
        self.tree.delete(self.tree.selection())
        self.sqlapi.delete_server(select_server)

    def save_settings(self):
        self.sqlapi.update_settings({"interval": self.entry_interval.get(),
                                  "count_of_check": self.entry_numcheck.get(),
                                   "email": self.entry_email.get()
                                     })
        self.quit()

    def get_settings(self):
        interval, count_of_check, email = self.sqlapi.get_settings()
        self.entry_interval.insert(0, str(interval))
        self.entry_numcheck.insert(0, str(count_of_check))
        self.entry_email.insert(0, email)

    def create_toplevel(self, server='', state=''):
        Dialog(self, server, state, self.edit)

if __name__ == '__main__':
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    table = Table(root)
    root.mainloop()