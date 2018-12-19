"""
Модуль содердит класс DialogService
"""
from tkinter import *
from tkinter import ttk
import subprocess, ctypes, psutil, time, os


class DialogService (Frame, object):
    """
    Класс DialogService содержит методы для работы со службой приложения
    """
    def __init__(self):
        """
        Метод __init__ инициализирует создание экземпляра класса DialogService и создает пользовательский интерфейс
        :param master: Table
        """
        Frame.__init__(self)
        # Создание экземпляра класса Toplevel
        # self.master = master
        self.toplevel_dialog = Toplevel()
        self.toplevel_dialog.minsize(300, 100)
        self.toplevel_dialog.protocol("WM_DELETE_WINDOW", self.close_toplevel)
        # Установка заголовка окна (зависит от того, редактируется запись или создается новая
        self.toplevel_dialog.title("Настройки службы")
        # Сделать окно модальным
        self.toplevel_dialog.grab_set()
        self.toplevel_dialog.focus_set()
        self.exec_file = os.path.join(os.getcwd(), "server_monitor_service.exe")

        # Контейнер для кнопок
        container_buttons = ttk.Frame(self.toplevel_dialog)
        container_buttons.pack(fill='x', side=TOP, pady=10, padx=(10, 10))
        self.install_service_button = ttk.Button(container_buttons, text='Установить службу',
                                                 command=self.install_service)
        self.install_service_button.pack(side=TOP, fill='x', expand=True, pady=3)
        self.start_service_button  = ttk.Button(container_buttons, text='Запустить службу', command=self.start_service)
        self.start_service_button.pack(side=TOP, fill='x', expand=True, pady=3)
        self.stop_service_button  = ttk.Button(container_buttons, text='Остановить службу', command=self.stop_service)
        self.stop_service_button.pack(side=TOP, fill='x', expand=True, pady=3)
        self.delete_service_button  = ttk.Button(container_buttons, text='Удалить службу', command=self.remove_service)
        self.delete_service_button.pack(side=TOP, fill='x', expand=True, pady=3)
        self.close_button = ttk.Button(container_buttons, text='Закрыть', command=self.close_toplevel)
        self.close_button.pack(side=LEFT, fill='x', expand=True, pady=3)
        self.check_state_service()

    def check_state_service(self):
        """
        Метод check_state включает и отключает кнопки в зависимости от состояния службы
        :return: None
        """
        try:
            service = psutil.win_service_get('server_monitor')
            if service and service.status() == 'running':
                self.install_service_button.config(state=DISABLED)
                self.start_service_button.config(state=DISABLED)
                self.stop_service_button.config(state=NORMAL)
                self.delete_service_button.config(state=DISABLED)
            else:
                self.install_service_button.config(state=DISABLED)
                self.start_service_button.config(state=NORMAL)
                self.stop_service_button.config(state=DISABLED)
                self.delete_service_button.config(state=NORMAL)
        except Exception as e:
            self.install_service_button.config(state=NORMAL)
            self.start_service_button.config(state=DISABLED)
            self.stop_service_button.config(state=DISABLED)
            self.delete_service_button.config(state=DISABLED)




    def close_toplevel(self):
        """
        Функция close_toplevel закрывает окно
        :return: None
        """
        self.toplevel_dialog.destroy()

    def is_admin(self):
        """
        Метод is_admin проверяет - является ли пользователь администратором
        :return: boolean
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_or_delete_reg_key(self):
        """
        Метод create_or_delete_reg_key создает или удаляет записи в реестре в зависимости от состояния службы
        :return:
        """
        with open(os.path.join(os.getcwd(), "monitor.log"), 'a') as f:
            try:
                if self.is_admin():
                    subprocess.run('python.exe' + ' ' + os.path.join(os.getcwd(), "reg.py"))
                else:
                    ctypes.windll.shell32.ShellExecuteW(None, 'runas', 'python.exe', os.path.join(os.getcwd(), "reg.py"), None, 1)
            except Exception as err:
                f.write(str(err))

    def do_action(self, action):
        """
        Метод do_action запускает исполняемый файл службы приложения с переданным в параметре аргументом
        :param action: str
        :return: None
        """
        with open(os.path.join(os.getcwd(), "monitor.log"), 'a') as f:
            try:
                if self.is_admin():
                    subprocess.run(self.exec_file + ' ' + action)
                else:
                    ctypes.windll.shell32.ShellExecuteW(None, 'runas', self.exec_file, action, None, 1)

                time.sleep(20)
                self.check_state_service()
            except Exception as err:
                f.write(str(err))

    def install_service(self):
        """
        Метод install_service устанавливает службу
        :return: None
        """
        self.create_or_delete_reg_key()
        self.do_action('install')
        self.check_state_service()

    def start_service(self):
        """
        Метод start_service запускает службу
        :return: None
        """
        self.do_action('start')
        self.check_state_service()

    def stop_service(self):
        """
        Метод stop_service останавливает службу
        :return: None
        """
        self.do_action('stop')
        self.check_state_service()

    def remove_service(self):
        """
        Метод remove_service удаляет службу
        :return: None
        """
        self.create_or_delete_reg_key()
        self.do_action('remove')
        self.check_state_service()
