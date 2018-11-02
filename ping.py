# -*- coding: utf8 -*-
import subprocess, platform
import time
from threading import Thread
from sqlapi import DB

# class Ping(Thread):
class Ping():
    def __init__(self, name):
        # Thread.__init__(self)
        # self.host = host
        self.name = name
        self.sqlapi = DB()

    def run(self):
        """
        Returns True if host responds to a ping request
        """

        interval, count_of_check, email = self.sqlapi.get_settings()

        subprocess.call("chcp 65001", shell=True)
        # Ping
        while True:
            # 1. Запросить список серверов в базе
            servers = self.sqlapi.get_servers()
            for server in servers:
                host = server[0]
                state = server[1]
                error_count = int(server[2])

                # Ping parameters as function of OS
                ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
                args = "ping " + " " + ping_str + " " + host
                with open('PingService.log', 'a') as f:
                    # Результат проверки
                    check_res = subprocess.call(args,  stdout=f) == 0
                    # Если сервер недоступен, но пока не установлен флаг аварийности (state == ERROR)
                    if (not check_res) & (state == "OK"):
                        # Увеличить счетчик ошибок на 1 и обновить счетчик в базе данных
                        error_count += 1
                        self.sqlapi.update_error_count({"name": host, "error_count": error_count})

                    # Если state == OK  и error_count >= count_of_check - записать в базу state == ERROR
                    # и отправить сообщение о том, что сервер недоступен
                    if (error_count >= count_of_check) &  (state == "OK"):
                        print("Сервер", host, " недоступен в течении ", interval * count_of_check, "секунд")
                        self.sqlapi.update_state({"name": host, "state": "ERROR"})

                    # Если state == Error  и check_res == 0 - записать в базу state == OK, обнулить счетчик ошибок
                    # и отправить сообщение, что сервер снова доступен
                    if (state == "Error") & check_res:
                        print("Сервер", host, " снова доступен", interval * count_of_check, "секунд")
                        error_count = 0
                        self.sqlapi.update_error_count({"name": host, "state": "ОК"})
                        self.sqlapi.update_error_count({"name": host, "error_count": error_count})

                # Здесь интервал из настроек (из базы)
            time.sleep(interval)

# test call
# print(datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S"),  file=open('ping.txt', 'a+'))
th = Ping("ping")
th.run()