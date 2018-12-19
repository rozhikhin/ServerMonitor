# -*- coding: utf8 -*-
"""
Модуль содержит класс
"""
import subprocess, platform, winreg
import datetime
from send_mail import RAMail
from sqlapi import DB

class Ping():
    """
    Класс Ping содержит методы для проверки доступности серверов
    """
    def __init__(self):
        """
        Инициализация переменных
        """
        # Ключ реестра, в котором будут храгиться записи
        self.reg_key = r'Software\Rozhikhin\ServerMonitor'
        # Получить данные из реестра
        self.regdata = self.read_from_reg()
        # Лог
        self.log = self.regdata['log']
        # База данных
        self.db = self.regdata['db']
        # Экземпляр класа для работы с базой данных
        self.sqlapi = DB(self.db)
        # Экземпляр класа для работы с базой данных
        self.mail = RAMail()
        # Наличие ошибок при отправке почты
        self.error_mail = False

    def read_from_reg(self):
        """
        Метод read_from_reg получает данные из реестра
        :return: dict
        """
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.reg_key, 0, winreg.KEY_ALL_ACCESS)
            db = winreg.QueryValueEx(key, "DB_FILE")
            log = winreg.QueryValueEx(key, "LOG_FILE")
            winreg.CloseKey(key)
            return {'db' : db[0], 'log' : log[0] }
        except Exception as err:
            print(str(err), file=self.log)

    def check_ping(self, host):
        """
        Метод check_ping пингует указанный хост и возращает 0 в случае успеха и 1 - если хост не доступен
        :param host: str
        :return: code: int
        """
        ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
        args = "ping " + " " + ping_str + " " + host

        with subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as proc:
            output = proc.communicate()[0]
            output = output.decode("cp866", "ignore")
            code = proc.returncode
            if ('unreachable' in str(output) or ('недоступен' in str(output))):
                code = 1
        return code

    def run(self):
        """
        Метод run проверяет доступность хостов по списку, полученному из базы данных и отправляет сообщение на почту
        в случае изменеия состояния сервера
        :return:
        """
        with open(self.log, 'a') as log:
            # Получить настройки для из БД для отправки почты
            self.interval, count_of_check, email_from, email_to, password_hash, smtp_server, smtp_port, start_tls = self.sqlapi.get_settings()
            # Если данные корректные
            if all([email_from, email_to, password_hash, smtp_server]):
                # subprocess.call("chcp 65001", shell=True, stdout=subprocess.DEVNULL)
                # Запросить список серверов в базе
                servers = self.sqlapi.get_servers()
                for server in servers:
                    # Для кажого сервера
                    host = server[0]
                    state = int(server[1])
                    error_count = int(server[2])
                    check_res = self.check_ping(host)

                    # Если сервер не прошел проверку (check_res != 0) и отмечен в БД как рабочий (state == 0)
                    if (check_res != 0) and (state == 0):
                        # Записать информацию в лог
                        print(datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S"), file=log)
                        print("Сервер ", host, " недоступен.",  file=log)
                        # Увеличить счетчик ошибок на 1 и обновить счетчик в базе данных
                        error_count += 1
                        self.sqlapi.update_error_count({"name": host, "error_count": error_count})

                    # Если количество ошибок для данного сервера равно или больше максимально допустимого  и сервер
                    # значится в БД как рабочий (state ==  0) - изменить состояние севрера в БД на аварийное
                    # (state ==  1) и отправить сообщение
                    if (error_count >= count_of_check) and  (state == 0):
                        text = "Сервер " + host + " недоступен в течении " + str(self.interval * count_of_check) + " секунд"
                        print(datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S"), file=log)
                        print(text, file=log)
                        self.mail.send(smtp_server, email_from, password_hash, email_from, email_to, "Сервер недоступен", text)
                        self.sqlapi.update_state({"name": host, "state": 1})

                    # Если сервер значится в БД как аварийный (state == 1), но стал снова отвечать на запросы -
                    # изменить состояние сервера на рабочее (state == 0), обнулить счетчик ошибок в БД и
                    # отправить соответсвующее сообщение
                    if (state == 1) and check_res == 0:
                        print(datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S"), file=log)
                        text = "Сервер " + host + " снова доступен "
                        print(text, file=log)
                        self.mail.send(smtp_server, email_from, password_hash, email_from, email_to, "Сервер  " + host + " снова доступен",
                                       text)
                        error_count = 0
                        self.sqlapi.update_state({"name": host, "state": 0})
                        self.sqlapi.update_error_count({"name": host, "error_count": error_count})
            else:
                # Иначе записать в лог ошибку
                if not self.error_mail:
                    print("Не вснесены все реквизиты в базу данных", file=log)
                    self.error_mail = True