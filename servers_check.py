# -*- coding: utf8 -*-
import subprocess, platform
import time
# from threading import Thread, Timer
from sqlapi import DB

# class Ping(Thread):
class Ping():
    def __init__(self, name):
        # Thread.__init__(self)
        # self.host = host
        self.name = name
        self.sqlapi = DB()

    # def run(self):
    #     from threading import Timer
    #     t = Timer(10, self.ping, args=None, kwargs=None)
    #     t.start()

    def check_ping(self, host):
        # Ping parameters as function of OS
        ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
        args = "ping " + " " + ping_str + " " + host
        # need_sh = False if platform.system().lower() == "windows" else True

        # log_file = 'C:\\TestService.log'
        # with open(log_file, 'a', encoding="utf-8") as f:
        with subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as proc:
            output = proc.communicate()[0]
            output = output.decode("cp866", "ignore")
            code = proc.returncode
            if ('unreachable' in str(output) or ('недоступен' in str(output))):
                code = 1
            print('code = '  + str(code))
        return code

    def run(self):
        interval, count_of_check, email = self.sqlapi.get_settings()
        subprocess.call("chcp 65001", shell=True, stdout=subprocess.DEVNULL)
        while True:
            # Запросить список серверов в базе
            servers = self.sqlapi.get_servers()
            for server in servers:

                host = server[0]
                state = int(server[1])
                error_count = int(server[2])

                print(host, state, error_count)

                check_res = self.check_ping(host)
                print(check_res)
                # if (not check_res and state == "ОК"):
                if (check_res != 0) and (state == 0):
                    # Увеличить счетчик ошибок на 1 и обновить счетчик в базе данных
                    error_count += 1
                    self.sqlapi.update_error_count({"name": host, "error_count": error_count})

                if (error_count >= count_of_check) and  (state == 0):
                    print("Сервер", host, " недоступен в течении ", interval * count_of_check, "секунд") # Заменить на отправку сообщения по почте
                    self.sqlapi.update_state({"name": host, "state": 1})

                if (state == 1) and check_res == 0:
                    print("Сервер", host, " снова доступен.") # Заменить на отправку сообщения по почте
                    error_count = 0
                    self.sqlapi.update_state({"name": host, "state": 0})
                    self.sqlapi.update_error_count({"name": host, "error_count": error_count})

            time.sleep(interval)

# test call
# print(datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S"),  file=open('ping.txt', 'a+'))
# th = Ping("ping")
# th.run()