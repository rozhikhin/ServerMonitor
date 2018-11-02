from tkinter import *
from tkinter import ttk
from dialog import Dialog
from tkinter import messagebox
from sqlapi import DB
from service_dialog import DialogService
import re

class Table(Frame, object):
    def __init__(self, master):
        """
        Функция __init__ инициализирует необхожимые переменные класса и содержит конструкто класса
        :param master: ссылка на родительский элемент
        """
        Frame.__init__(self)
        # Инициализация перменных
        # Элемент Treeview, содержащий список сервреров
        self.tree = None
        # Данные, приходящие из дочернего окна
        self.toplevel_data = None
        # Редактируется ли запись (self.edit = True) или создается новая (self.edit = False)
        self.edit = False
        # Ссылка на объект класса DБ, содержащего методы для работы с классами
        self.sqlapi = DB()
        # Создание базы данных
        self.sqlapi.init_db()
        # Создание интерфейса главнго окна приложения
        self.setup_ui()
        # Добавление списка серверов из БД
        self.add_all_servers()
        # Получение настроек программы из БД
        self.get_settings()

    def setup_ui(self):
        """
        Функция setup_ui создает пользовательский интерфейс главного окна приложения
        :return: None
        """

        # Контейнер для элемента Treeview
        container = ttk.Frame()
        container.pack(fill='x', side=TOP, pady=10, padx=5, expand=False)
        # Создание Treeview, содержащего список серверов
        self.tree = ttk.Treeview(container, columns=("columns1","columns2"), show="headings")
        # self.tree = ttk.Treeview(container, columns=("columns1","columns2","columns3"))
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        # Заголовки колонок
        self.tree.heading("#1", text="Сервер")
        self.tree.heading("#2", text="Состояние")
        # self.tree.heading("#3", text="Ошибки")
        # Подключение обработчика при выделении элемента
        self.tree.bind("<<TreeviewSelect>>", self.select)
        self.tree.pack()

        # Отступ для кнопок
        padx_button = 25
        # Контейнер для кнопок
        container2 = ttk.Frame()
        container2.pack(fill='x', side=TOP, pady=10, padx=10)
        # Кнопка изменения записи
        button_exit = Button(container2, text="Изменить", width=15, command=self.create_top_for_edit_server)
        button_exit.pack(side=LEFT, padx=(0,padx_button))
        # Кнопка добавления записи
        button_add = Button(container2, text="Добавить", width=15, command=self.create_top_for_add_server)
        button_add.pack(side=LEFT, padx=(0,padx_button))
        # Кнопка удаления записи
        button_del = Button(container2, text="Удалить", width=15, command=self.remove_server)
        button_del.pack(side=LEFT, padx=(0,padx_button))

        # Контейнер для вывода сообщения об ошибках
        container_info = ttk.Frame()
        container_info.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        # Label для вывода записи об ошибках заполнения полей
        self.label_message = Label(container_info, text="", fg='Red')
        # Не размещать запись, если нет ощибок
        self.label_message.pack_forget()

        # Контейнер для надписи и поля ввода для настройки интервала проверки
        container_interval = ttk.Frame()
        container_interval.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_interval = Label(container_interval, text="Интервал")
        label_interval.pack( side=LEFT, padx=5)
        # Поле ввода с проверкой - в фокусе ли ввода элемент (validate='focusin').
        # Если да, то срабатывает метод set_default_style.
        self.entry_interval = Entry(container_interval, width=10, validate='focusin', validatecommand=self.set_default_style)
        self.entry_interval.pack( side=RIGHT, padx=(0, 200))

        # Контейнер для надписи и поля ввода для настройки количества проверок до признания сервера аварийным
        # и отправки соответствующего сообщения
        container_numcheck = ttk.Frame()
        container_numcheck.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_numcheck = Label(container_numcheck, text="Количество проверок")
        label_numcheck.pack( side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_numcheck = Entry(container_numcheck, width=10, validate='focusin', validatecommand=self.set_default_style)
        self.entry_numcheck.pack( side=RIGHT, padx=(0, 200))

        # Контейнер для надписи и поля ввода для e-mail для отправки сообщений
        container_email = ttk.Frame()
        container_email.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_email = Label(container_email, text="E-Mail")
        label_email.pack( side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_email = Entry(container_email, width=50, validate='focusin', validatecommand=self.set_default_style)
        self.entry_email.pack( side=RIGHT, padx=(0, 0))

        # Контейнер для кнопок формы настроек
        container3 = ttk.Frame()
        container3.pack(fill='x', side=TOP, pady=10, padx=10)
        # Кнопка закрытия формы настроек
        button_exit = Button(container3, text="Выйти", width=15, command=root.quit)
        button_exit.pack(side=RIGHT, padx=(0, padx_button))
        # Кнопка сохранения настроек
        self.button_save = Button(container3, text="Сохранить", width=15, command=self.save_settings)
        self.button_save.pack(side=RIGHT, padx=(0, padx_button))
        # Кнопка запуска проверки
        button_check = Button(container3, text="Служба", width=15, command=self.open_service_settings)
        button_check.pack(side=RIGHT, padx=(0, padx_button))

    def select(self, event=None):
        """
        Функция select при выделении элемента в Treeview возвращает словарь с данными выделенного элемента
        :param event: None
        :return: dict
        """
        for nm in self.tree.selection():
            server_name, state, err = self.tree.item(nm, 'values')
        return {'server_name': server_name, 'state': state}

    def add_all_servers(self):
        """
        Функция add_all_servers получает из базы данных список с данными серверов, сортирует его и добавляет в Treeview
        :return: None
        """
        servers = self.sqlapi.get_servers()
        servers.sort()
        if servers is not None:
            for values in servers:
                self.tree.insert("", END, values=values)

    def create_top_for_add_server(self):
        """
        Функция create_top_for_add_server создает и показыыает окно для добавления сервера
        :return: None
        """
        self.edit = False
        Dialog(self)

    def create_top_for_edit_server(self):
        """
        Функция create_top_for_add_server создает и показыыает окно для редактирования сервера
        :return: None
        """
        # Устанавливает флаг edit, означающий что диалоговое окно открывается для редактирования
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
        """
        Функция sort_servers_list сортирует список сервероа в Treeview после добавления или редактирования сервера
        :param server_data: dict
        :return: None
        """
        # Создаем пустой список
        servers = list()
        # Добавляем в список новый сервер
        servers.append((server_data["server_name"], server_data["state"]))
        # Получаем и перебираем все элементы в списке серверов.
        for item in self.tree.get_children():
            server, state, err = self.tree.item(item, 'values')
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
        """
        Функция save_server сохраняет данные после добавления или редактирования сервера
        :param server_data: dict
        :return: None
        """
        if self.edit:
            self.edit_server(server_data)
        else:
            self.add_server(server_data)

    def remove_server(self):
        """
        Функция remove_server удаляет сервер
        :return: None
        """
        select_server = self.select()
        self.tree.delete(self.tree.selection())
        self.sqlapi.delete_server(select_server)

    def save_settings(self):
        """
        Функция save_settings проверяет корректность введенных данных и сохраняет настройки в базе данных
        :return: None
        """
        # Сообщение, которое выводится при некорректном заполнении полей в форме настроек
        msg = 'Неверно заполнено поле '
        # Флаг. Если True, то на форме будет выводиться выодиться сообщение msg
        error = False
        # Словарь со значеиями введенных настроек
        entry_text_dict = {
                        "interval": self.entry_interval.get(),
                        "count_of_check": self.entry_numcheck.get(),
                        "email": self.entry_email.get()
        }
        # Если поле пустое или не является числом
        if not entry_text_dict["interval"].isnumeric():
            # Сделать фон поля красным
            self.entry_interval.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если поле пустое или не является числом
        if not entry_text_dict["count_of_check"].isnumeric():
            # Сделать фон поля красным
            self.entry_numcheck.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если поле не является корректным e-mail адресом
        if not self.check_email(entry_text_dict["email"]):
            # Сделать фон поля красным
            self.entry_email.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если флаг error установлен в True
        if error:
            # Установить фокус на кнопку "Сохранить"
            self.button_save.focus()
            # Показать сообщение об ошибке
            self.label_message.pack(side=LEFT, padx=(100, 0))
            self.label_message.config(text=msg)
            return
        # Сохранить настройки в базе данных
        self.sqlapi.update_settings(entry_text_dict)
        self.quit()

    def get_settings(self):
        """
        Функция get_settings получает настройки из базы данные и отображает их в поях формы
        :return: None
        """
        interval, count_of_check, email = self.sqlapi.get_settings()
        self.entry_interval.insert(0, str(interval))
        self.entry_numcheck.insert(0, str(count_of_check))
        self.entry_email.insert(0, email)

    def set_default_style(self):
        """
        Функция set_default_style возвращает виджетам фон по умолчанию
        :return: Bool
        """
        self.entry_interval.configure(bg="White")
        self.entry_numcheck.configure(bg="White")
        self.entry_email.configure(bg="White")
        # Метод проверки должен вернуть True, чтобы разрешить изменение (т.е. проверка будет выпоняться каждый раз при наступлении события,
        # False, чтобы отклонить его ( т.е. проверка не будет выполняться)
        # или None, чтобы отключить себя (проверка будет выпонена 1 раз и потом будет оключена).
        return True

    def check_email(self, email):
        """
        Функция check_email проверяет корректность введенного e-mail
        :param email: str
        :return: Bool
        """
        exp = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        res = re.search(exp, email)
        if res:
            return True
        return False

    def open_service_settings(self):
        """
        Функция open_service_settings открывает окно с настройками службы Windows
        :return: None
        """
        DialogService()


if __name__ == '__main__':
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    table = Table(root)
    root.mainloop()