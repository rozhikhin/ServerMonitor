from tkinter import *
from tkinter import ttk


class DialogService (Frame, object):
    # def __init__(self, master):
    def __init__(self):
        """
        Функция __init__ инициализирует создание экземпляра класса DialogService и создает пользовательский интерфейс
        :param master: Table
        """
        # Frame.__init__(self, master)
        Frame.__init__(self)
        # Создание экземпляра класса Toplevel
        # self.master = master
        self.toplevel_dialog = Toplevel()
        self.toplevel_dialog.minsize(300, 100)
        self.toplevel_dialog.protocol("WM_DELETE_WINDOW", self.close_toplevel)
        # self.toplevel_dialog.transient(master)
        # Установка заголовка окна (зависит от того, редактируется запись или создается новая
        self.toplevel_dialog.title("Настройки службы")
        # Сделать окно модальным
        self.toplevel_dialog.grab_set()
        self.toplevel_dialog.focus_set()

        # Контейнер для кнопок
        container_buttons = ttk.Frame(self.toplevel_dialog)
        container_buttons.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.install_service_button = ttk.Button(container_buttons, text='Установить службу')
        self.install_service_button.pack(side=TOP, fill='x', expand=True)
        self.start_service_button  = ttk.Button(container_buttons, text='Запустить службу')
        self.start_service_button .pack(side=TOP, fill='x', expand=True)
        self.stop_service_button  = ttk.Button(container_buttons, text='Остановить службу')
        self.stop_service_button .pack(side=TOP, fill='x', expand=True)
        self.delete_service_button  = ttk.Button(container_buttons, text='Удалить службу')
        self.delete_service_button .pack(side=TOP, fill='x', expand=True)
        self.close_button = ttk.Button(container_buttons, text='Закрыть', command=self.close_toplevel)
        self.close_button.pack(side=LEFT, fill='x', expand=True)


    def close_toplevel(self):
        """
        Функция close_toplevel закрывает окно
        :return: None
        """
        self.toplevel_dialog.destroy()


if __name__ == '__main__':
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    DialogService()
    # table = Table(root)
    root.mainloop()


