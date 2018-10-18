from tkinter import *
from tkinter import ttk
from dialog import Dialog
from tkinter import messagebox
from sqlapi import DB
import re

class Table(Frame, object):
    def __init__(self, master):
        Frame.__init__(self)
        # Инициализация перменных
        # Таблица со списком серверов
        self.tree = None
        # Дочернее окно для редактирования и добавления записей
        # Данные, приходящие из дочернего окна
        self.toplevel_data = None
        # Редактируется ли запись (self.edit = True) или создается новая (self.edit = False)
        self.edit = False
        self.servers = list()
        self.sqlapi = DB()
        self.sqlapi.init_db()
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
        button_exit = Button(container2, text="Изменить", width=15, command=self.create_top_for_edit_server)
        button_exit.pack(side=LEFT, padx=(0,padx_button))
        button_add = Button(container2, text="Добавить", width=15, command=self.create_top_for_add_server)
        button_add.pack(side=LEFT, padx=(0,padx_button))
        button_del = Button(container2, text="Удалить", width=15, command=self.remove_server)
        button_del.pack(side=LEFT, padx=(0,padx_button))

        container_info = ttk.Frame()
        container_info.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        self.label_message = Label(container_info, text="", fg='Red')
        self.label_message.pack_forget()
        # self.label_message_interval.pack(side=LEFT, padx=(100, 0))

        container_interval = ttk.Frame()
        container_interval.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_interval = Label(container_interval, text="Интервал")
        label_interval.pack( side=LEFT, padx=5)
        self.entry_interval = Entry(container_interval, width=10, validate='focusin', validatecommand=self.set_default_style)
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
        self.button_save = Button(container3, text="Сохранить", width=15, command=self.save_settings)
        self.button_save.pack(side=RIGHT, padx=(0, padx_button))
        button_del = Button(container3, text="Отмена", width=15)
        button_del.pack(side=RIGHT, padx=(0, padx_button))

    def select(self, event=None):
        for nm in self.tree.selection():
            server_name, state = self.tree.item(nm, 'values')
        return {'server_name': server_name, 'state': state}

    def add_all_servers(self):
        servers = self.sqlapi.get_servers()
        servers.sort()
        if servers is not None:
            for values in servers:
                self.tree.insert("", END, values=values)

    def create_top_for_add_server(self):
        self.edit = False
        Dialog(self)

    def create_top_for_edit_server(self):
        self.edit = True
        server, state = ('', '')
        for nm in self.tree.selection():
            server, state = self.tree.item(nm, 'values')
        if server:
            dialog = Dialog(self, server, state, title="Редактировать запись")
        else:
            messagebox.showinfo("Выберите сервер", "Необходимо выбрать сервер для редактирования")

    def add_server(self, server_data):
        """
        Функция add_server принимает словарь из имени сервера и состояния.
        Сохраняет новую запись в базе и добавляет ее в список серверов в приложении и сортирует его
        :param server_data: dict
        :return: None
        """
        # Проверяем, что сохранение в базу данные прошло успешно
        if self.sqlapi.save_server(server_data):
            self.sort_serevrs_list(server_data)

    def edit_server(self, server_data):
        """
        Функция edit_server принимает словарь из имени сервера и состояния.
        Сохраняет измененную запись в базе и добавляет ее в список серверов в приложении и сортирует его
        :param server_data: dict
        :return: None
        """
        # Добавим к словарю старое имя сервера, которое нужно заменить
        server_data['old_name'] = self.select()['server_name']
        # Удаляем из списка старое имя сервера
        self.tree.delete(self.tree.selection())
        if self.sqlapi.update_server(server_data):
            self.sort_serevrs_list(server_data)

    def sort_serevrs_list(self, server_data):
        # Создаем пустой список
        servers = list()
        # Добавляем в список новый сервер
        servers.append((server_data["server_name"], server_data["state"]))
        # Получаем и перебираем все элементы в списке серверов.
        for item in self.tree.get_children():
            server, state = self.tree.item(item, 'values')
            # Проверяем, что новое имя сервера уникально - для новой записи
            if (not self.edit) and (server_data["server_name"] == server):
                return
            # Добавляем каждую запись в список
            servers.append((server, state))
        # Сортируем список
        servers.sort()
        # Удаляем все записи из списка серверов
        self.tree.delete(*self.tree.get_children())
        # И снова добавляем их в отсортированном виде
        for values in servers:
            self.tree.insert("", END, values=values)


    def save_server(self, server_data):
        if self.edit:
            self.edit_server(server_data)
        else:
            self.add_server(server_data)

    def remove_server(self):
        select_server = self.select()
        self.tree.delete(self.tree.selection())
        self.sqlapi.delete_server(select_server)

    def save_settings(self):
        msg = 'Неверно заполнено поле '
        error = False
        entry_text_dict = {
                        "interval": self.entry_interval.get(),
                        "count_of_check": self.entry_numcheck.get(),
                        "email": self.entry_email.get()
        }
        if not entry_text_dict["interval"].isnumeric():
            self.entry_interval.config({"background": "Red"})
            error = True
        if not entry_text_dict["count_of_check"].isnumeric():
            self.entry_numcheck.config({"background": "Red"})
            error = True
        if not self.check_email(entry_text_dict["email"]):
            self.entry_email.config({"background": "Red"})
            error = True
        if error:
            self.button_save.focus()
            self.label_message.pack(side=LEFT, padx=(100, 0))
            self.label_message.config(text=msg)
            return
        self.sqlapi.update_settings(entry_text_dict)
        self.quit()

    def get_settings(self):
        interval, count_of_check, email = self.sqlapi.get_settings()
        self.entry_interval.insert(0, str(interval))
        self.entry_numcheck.insert(0, str(count_of_check))
        self.entry_email.insert(0, email)

    # Вернуть виджету фон по умолчанию (если он получил фокус)
    def set_default_style(self):
        # self.toplevel_entry_server.config({"background": "White"})
        self.entry_interval.configure(bg="White")
        self.entry_numcheck.configure(bg="White")
        self.entry_email.configure(bg="White")
        # Метод проверки должен вернуть True, чтобы разрешить изменение (т.е. проверка будет выпоняться каждый раз при наступлении события,
        # False, чтобы отклонить его ( т.е. проверка не будет выполняться)
        # или None, чтобы отключить себя (проверка будет выпонена 1 раз и потом будет оключена).
        return True

    def check_email(self, email):
        exp = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        res = re.search(exp, email)
        if res:
            return True
        return False


if __name__ == '__main__':
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    table = Table(root)
    root.mainloop()