from tkinter import *
import tkinter as tk
from tkinter import ttk

class Dialog(Frame, object):
    def __init__(self, master, server="", state="", title="Добавить запись"):
        """
        Функция __init__ инициализирует создание экземпляра класса Dialog и создает пользовательский интерфейс
        :param master: Table
        :param server: str
        :param state: str
        :param title: str
        """
        Frame.__init__(self, master)

        # Список и словарь для выпадающего списка. Сисок для заполнения занчениями выпадающий список.
        # Словарь - числовые соответсвия значениям списка
        # define keys and mappings
        self.ITEMS = ["OK", "ERROR"]
        self.MAPPING = {"ERROR" : 1, "OK" : 0}

        # Создание экземпляра класса Toplevel
        self.master = master
        self.toplevel_dialog = Toplevel()
        self.toplevel_dialog.minsize(300, 100)
        self.toplevel_dialog.protocol("WM_DELETE_WINDOW", self.close_toplevel)
        self.toplevel_dialog.transient(master)
        # Установка заголовка окна (зависит от того, редактируется запись или создается новая
        self.toplevel_dialog.title(title)
        # Сделать окно модальным
        self.toplevel_dialog.grab_set()
        self.toplevel_dialog.focus_set()

        # Контейнер с надписью и полем для имени сервера
        container_server = ttk.Frame(self.toplevel_dialog)
        container_server.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.toplevel_dialog_label = ttk.Label(container_server, text='Сервер')
        self.toplevel_dialog_label.pack(side=LEFT)
        # Проверка - если виджет получил фокус, то вызвать функцию - set_default_style, которая вернет виджету фон по-умолчанию
        self.toplevel_entry_server = Entry(container_server, width=33,  validate='focus', validatecommand=self.set_default_style)
        self.toplevel_entry_server.insert(0, server)
        self.toplevel_entry_server.pack(side=RIGHT)

        # Контейнер с надписью и выпадающим спискок для указания состояния сервера
        container_state = ttk.Frame(self.toplevel_dialog)
        container_state.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.toplevel_dialog_label = ttk.Label(container_state, text='Состояние')
        self.toplevel_dialog_label.pack(side=LEFT)
        self.toplevel_combobox_state = ttk.Combobox(container_state, width=30, values=self.ITEMS, state='readonly')
        self.toplevel_combobox_state.current(0)
        self.toplevel_combobox_state.pack(side=RIGHT)
        # self.toplevel_combobox_state.bind('<<ComboboxSelected>>', self.onSelect)

        # Контейнер для кнопок
        container_buttons = ttk.Frame(self.toplevel_dialog)
        container_buttons.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.toplevel_dialog_yes_button = ttk.Button(container_buttons, text='Сохранить', command=self.get_text)
        self.toplevel_dialog_yes_button.pack(side=LEFT, fill='x', expand=True)
        self.toplevel_dialog_no_button = ttk.Button(container_buttons, text='Отмена', command=self.close_toplevel)
        self.toplevel_dialog_no_button.pack(side=LEFT, fill='x', expand=True)

    # def onSelect(self, event):
    #     print(self.MAPPING[self.toplevel_combobox_state.get()])

    def get_text(self):
        """
        Функция get_text получает данные из полей формы и сохраняет данные
        :return: None
        """
        # Получаем имя сервера и приводим его к верхнему регистру
        server_name = self.toplevel_entry_server.get().upper().strip()
        # Если поле с именем сервера пустое, то кстановить фон поля ввода красного цвета и остановить обработку
        if not server_name:
            self.toplevel_entry_server.config({"background": "Red"})
            return
        state = self.MAPPING[self.toplevel_combobox_state.get()]
        # print(state)

        # Вызываем функцию главного модуля и сохраняем данные
        self.master.save_server({"server_name": server_name, "state": state})
        self.close_toplevel()

    def set_default_style(self):
        """
        Функция set_default_style возвращает виджету фон по умолчанию (если он получил фокус)
        :return: bool
        """
        self.toplevel_entry_server.configure(bg="White")
        # Метод проверки должен вернуть True, чтобы разрешить изменение (т.е. проверка будет выпоняться каждый раз при наступлении события,
        # False, чтобы отклонить его ( т.е. проверка не будет выполняться)
        # или None, чтобы отключить себя (проверка будет выпонена 1 раз и потом будет оключена).
        return True

    def close_toplevel(self):
        """
        Функция close_toplevel закрывает окно
        :return: None
        """
        self.toplevel_dialog.destroy()




