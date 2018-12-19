from tkinter import *
from tkinter import ttk
from dialog import Dialog
from tkinter import messagebox
from sqlapi import DB
from send_mail import RAMail
from service_dialog import DialogService
import re, os


class Table(Frame, object):
    def __init__(self, master):
        """
        Метод __init__ инициализирует необхожимые переменные класса и содержит конструкто класса
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
        self.sqlapi = DB(os.path.join(os.getcwd(), "monitor.db"))
        self.mail = RAMail()
        # Создание базы данных
        self.sqlapi.init_db()
        # Создание интерфейса главнго окна приложения
        self.setup_ui()
        # Добавление списка серверов из БД
        self.add_all_servers()
        # Получение настроек программы из БД
        self.entry_text_dict = {}
        self.get_settings()


    def setup_ui(self):
        """
        Метод setup_ui создает пользовательский интерфейс главного окна приложения
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

        ##########################################################################

        # Контейнер для группировки виджетов

        group = LabelFrame(text="Настройка уведомлений", padx=5, pady=5)
        group.pack(padx=10, pady=10)

        # Контейнер для надписи и поля ввода для e-mail отправителя
        container_email_from = ttk.Frame(group)
        container_email_from.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_email_from = Label(container_email_from, text="E-Mail отправителя")
        label_email_from.pack( side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_email_from = Entry(container_email_from, width=40, validate='focusin', validatecommand=self.set_default_style)
        self.entry_email_from.pack( side=RIGHT, padx=(0, 0))

        # Контейнер для надписи и поля ввода для e-mail получателя
        container_email_to = ttk.Frame(group)
        container_email_to.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_email_from = Label(container_email_to, text="E-Mail получателя")
        label_email_from.pack( side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_email_to = Entry(container_email_to, width=40, validate='focusin', validatecommand=self.set_default_style)
        self.entry_email_to.pack( side=RIGHT, padx=(0, 0))

        # Контейнер для надписи и поля ввода пароля
        container_password = ttk.Frame(group)
        container_password.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_password = Label(container_password, text="Пароль")
        label_password.pack( side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_password = Entry(container_password, width=40, validate='focusin', validatecommand=self.set_default_style,  show="*")
        self.entry_password.pack( side=RIGHT, padx=(0, 0))

        # Контейнер для надписи и поля ввода подтверждения пароля
        container_confirm_password = ttk.Frame(group)
        container_confirm_password.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_confirm_password = Label(container_confirm_password, text="Подтверждение пароля")
        label_confirm_password.pack( side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_confirm_password = Entry(container_confirm_password, width=40, validate='focusin', validatecommand=self.set_default_style,  show="*")
        self.entry_confirm_password.pack( side=RIGHT, padx=(0, 0))

        # Контейнер для надписи и поля ввода SMTP сервера
        container_smtp_server = ttk.Frame(group)
        container_smtp_server.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_smtp_server = Label(container_smtp_server, text="SMTP сервер")
        label_smtp_server.pack( side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_smtp_server = Entry(container_smtp_server, width=40, validate='focusin', validatecommand=self.set_default_style)
        self.entry_smtp_server.pack( side=RIGHT, padx=(0, 0))

        # Контейнер для надписи и поля ввода SMTP порта
        container_smtp_port = ttk.Frame(group)
        container_smtp_port.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        label_smtp_port = Label(container_smtp_port, text="SMTP порт")
        label_smtp_port.pack(side=LEFT,padx=5)
        # Поле ввода с проверкой, аналогичной предыдущему полю
        self.entry_smtp_port = Entry(container_smtp_port, width=10, validate='focusin', validatecommand=self.set_default_style)
        self.entry_smtp_port.pack( side=RIGHT, padx=(0, 180))

        # Контейнер для надписи и checkbutton для указания - использовать tls или нет
        container_tls = ttk.Frame(group)
        container_tls.pack(fill='x', side=TOP, pady=5, padx=(10, 10))
        self.label_tls = Label(container_tls, text='Использовать TLS')
        self.label_tls.pack(side=LEFT,padx=5)
        self.tls = IntVar()
        self.checkbutton_tls = ttk.Checkbutton(container_tls, text = "", variable = self.tls)
        self.checkbutton_tls.pack(side=RIGHT, padx=(0, 225))

        #########################################################################

        # Контейнер для кнопок формы настроек
        container3 = ttk.Frame()
        container3.pack(fill='x', side=TOP, pady=10, padx=10)
        # Кнопка закрытия формы настроек
        button_exit = Button(container3, text="Выйти", width=15, command=root.destroy)
        button_exit.pack(side=RIGHT, padx=(0, padx_button))
        # Кнопка сохранения настроек
        self.button_save = Button(container3, text="Сохранить", width=15, command=self.save_settings)
        self.button_save.pack(side=RIGHT, padx=(0, padx_button))
        # Кнопка запуска проверки
        button_check = Button(container3, text="Служба", width=15, command=self.open_service_settings)
        button_check.pack(side=RIGHT, padx=(0, padx_button))

    def select(self, event=None):
        """
        Метод select при выделении элемента в Treeview возвращает словарь с данными выделенного элемента
        :param event: None
        :return: dict
        """
        server_name = None
        for nm in self.tree.selection():
            server_name, state = self.tree.item(nm, 'values')
        if not server_name:
            messagebox.showinfo("Выберите сервер", "Необходимо выбрать сервер ")
            return None
        return {'server_name': server_name, 'state': state}

    def convert_state_from_int_to_str(self, values):
        """
        Метод convert_state_from_int_to_str заменяет числовые значения на буквенные для пончтного отображние в форме
        :param values: tuple
        :return: list
        """
        values = list(values)
        if int(values[1]) == 0:
            values[1] = 'OK'
        else:
            values[1] = 'Error'
        return values

    def add_all_servers(self):
        """
        Метод add_all_servers получает из базы данных список с данными серверов, сортирует его и добавляет в Treeview
        :return: None
        """
        servers = self.sqlapi.get_servers_name_and_state()
        servers.sort()
        if servers is not None:
            for values in servers:
                values = self.convert_state_from_int_to_str(values)
                self.tree.insert("", END, values=values)

    def create_top_for_add_server(self):
        """
        Метод create_top_for_add_server создает и показыыает окно для добавления сервера
        :return: None
        """
        self.edit = False
        Dialog(self)

    def create_top_for_edit_server(self):
        """
        Метод create_top_for_add_server создает и показыыает окно для редактирования сервера
        :return: None
        """
        # Устанавливает флаг edit, означающий что диалоговое окно открывается для редактирования
        self.edit = True
        selected_data = self.select()
        if selected_data:
            server, state = selected_data["server_name"], selected_data["state"]
            Dialog(self, server, state, title="Редактировать запись")

    def add_server(self, server_data):
        """
        Метод add_server принимает словарь из имени сервера и состояния.
        Сохраняет новую запись в базе и добавляет ее в список серверов в приложении и сортирует его
        :param server_data: dict
        :return: None
        """
        # Проверяем, что сохранение в базу данные прошло успешно
        if self.sqlapi.save_server(server_data):
            self.sort_serevrs_list(server_data)

    def edit_server(self, server_data):
        """
        Метод edit_server принимает словарь из имени сервера и состояния.
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
        Метод sort_servers_list сортирует список сервероа в Treeview после добавления или редактирования сервера
        :param server_data: dict
        :return: None
        """

        if  server_data["state"] == 0:
            server_data["state"] = "OK"
        else:
            server_data["state"] = "ERROR"

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
        """
        Метод save_server сохраняет данные после добавления или редактирования сервера
        :param server_data: dict
        :return: None
        """
        if self.edit:
            self.edit_server(server_data)
        else:
            self.add_server(server_data)

    def remove_server(self):
        """
        Метод remove_server удаляет сервер
        :return: None
        """
        select_server = self.select()
        if select_server:
            self.tree.delete(self.tree.selection())
            self.sqlapi.delete_server(select_server)

    def field_fill_check(self):
        """
        Метод field_fill_check проверяет правильность заполнения полей формы настроек
        :return:  error: boolean
        """
        self.fill_dict_of_fields()
        msg = 'Не все поля заполнены'
        error = False
        # Если поле пустое или не является числом
        if not self.entry_text_dict["interval"].isnumeric():
            # Сделать фон поля красным
            self.entry_interval.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если поле пустое или не является числом
        if not self.entry_text_dict["count_of_check"].isnumeric():
            # Сделать фон поля красным
            self.entry_numcheck.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если поле пустое или не является числом
        if not self.entry_text_dict["smtp_port"].isnumeric():
            # Сделать фон поля красным
            self.entry_smtp_port.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если поле пустое
        if not self.entry_text_dict["password"]:
            # Сделать фон поля красным
            self.entry_password.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если пароли не совпадают
        if not self.entry_text_dict["password"] == self.entry_confirm_password.get():
            self.entry_password.config({"background": "Red"})
            self.entry_confirm_password.config({"background": "Red"})
            # self.msg += " \nПароль и подтверждение не совпадают"
            msg = "Пароль и подтверждение не совпадают"
            # Флаг error установить в значение True
            error = True
        # Если поле пустое
        if not self.entry_text_dict["smtp_server"]:
            # Сделать фон поля красным
            self.entry_smtp_server.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если поле не является корректным e-mail адресом
        if not self.check_email(self.entry_text_dict["email_from"]):
            # Сделать фон поля красным
            self.entry_email_from.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True
        # Если поле не является корректным e-mail адресом
        if not self.check_email(self.entry_text_dict["email_to"]):
            # Сделать фон поля красным
            self.entry_email_to.config({"background": "Red"})
            # Флаг error установить в значение True
            error = True

        if error:
            # Если флаг error установлен в True
            # Установить фокус на кнопку "Сохранить"
            self.button_save.focus()
            # Показать сообщение об ошибке
            self.label_message.pack(side=LEFT, padx=(100, 0))
            self.label_message.config(text=msg)
            return error

    def save_settings(self):
        """
        Метод save_settings проверяет корректность введенных данных и сохраняет настройки в базе данных
        :return: None
        """
        if self.field_fill_check():
            return
        # Сохранить настройки в базе данных
        self.entry_text_dict["password"] = self.mail.encode_password(self.entry_text_dict["password"])
        self.sqlapi.update_settings(self.entry_text_dict)
        self.quit()

    def get_settings(self):
        """
        Метод get_settings получает настройки из базы данные и отображает их в полях формы
        :return: None
        """
        interval, count_of_check, email_from, email_to, password_hash, smtp_server, smtp_port, start_tls = self.sqlapi.get_settings()
        self.entry_interval.insert(0, str(interval))
        self.entry_numcheck.insert(0, str(count_of_check))
        self.entry_email_from.insert(0, email_from)
        self.entry_email_to.insert(0, email_to)
        password = self.mail.decode_password(password_hash)
        self.entry_password.insert(0, password)
        self.entry_confirm_password.insert(0, password)
        self.entry_smtp_server.insert(0, smtp_server)
        self.entry_smtp_port.insert(0, str(smtp_port))
        self.tls.set(start_tls)

    def fill_dict_of_fields(self):
        """
        Метод fill_dict_of_fields заполняет словарь entry_text_dict данными из полей формы
        :return: None
        """
        # Словарь со значеиями введенных настроек
        self.entry_text_dict = {
                        "interval": self.entry_interval.get(),
                        "count_of_check": self.entry_numcheck.get(),
                        "email_from": self.entry_email_from.get(),
                        "email_to": self.entry_email_to.get(),
                        "password": self.entry_password.get(),
                        "smtp_server": self.entry_smtp_server.get(),
                        "smtp_port": self.entry_smtp_port.get(),
                        "tls": self.tls.get()
        }

    def set_default_style(self):
        """
        Метод set_default_style возвращает виджетам фон по умолчанию
        :return: Bool
        """
        self.entry_interval.configure(bg="White")
        self.entry_numcheck.configure(bg="White")
        self.entry_email_from.configure(bg="White")
        self.entry_email_to.configure(bg="White")
        self.entry_password.configure(bg="White")
        self.entry_confirm_password.configure(bg="White")
        self.entry_smtp_server.configure(bg="White")
        self.entry_smtp_port.configure(bg="White")
        self.label_message.pack_forget()

        # Метод проверки должен вернуть True, чтобы разрешить изменение (т.е. проверка будет выпоняться каждый раз при наступлении события,
        # False, чтобы отклонить его ( т.е. проверка не будет выполняться)
        # или None, чтобы отключить себя (проверка будет выпонена 1 раз и потом будет оключена).
        return True

    def check_email(self, email_from):
        """
        Метод check_email проверяет корректность введенного e-mail
        :param email: str
        :return: Bool
        """
        exp = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        res = re.search(exp, email_from)
        if res:
            return True
        return False

    def open_service_settings(self):
        """
        Метод open_service_settings открывает окно с настройками службы Windows
        :return: None
        """
        if self.field_fill_check():
            return
        DialogService()

if __name__ == '__main__':
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    table = Table(root)
    root.mainloop()