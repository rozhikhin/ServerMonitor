# -*- coding: utf8 -*-
import subprocess, platform, winreg
import datetime
from send_mail import RAMail
from sqlapi import DB

class Ping():
    def __init__(self):
        self.reg_key = r'Software\Rozhikhin\ServerMonitor'
        self.regdata = self.read_from_reg()
        self.log = self.regdata['log']
        self.db = self.regdata['db']
        self.sqlapi = DB(self.db)
        self.mail = RAMail()
        self.error_mail = False

    def read_from_reg(self):
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.reg_key, 0, winreg.KEY_ALL_ACCESS)
                db = winreg.QueryValueEx(key, "DB_FILE")
                log = winreg.QueryValueEx(key, "LOG_FILE")
                winreg.CloseKey(key)
                return {'db' : db[0], 'log' : log[0] }
            except Exception as err:
                print(str(err))

    def check_ping(self, host):
        # Ping parameters as function of OS
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
        with open(self.log, 'a') as log:
            self.interval, count_of_check, email_from, email_to, password_hash, smtp_server, smtp_port, start_tls = self.sqlapi.get_settings()
            if all([email_from, email_to, password_hash, smtp_server]):
                # subprocess.call("chcp 65001", shell=True, stdout=subprocess.DEVNULL)
                # Запросить список серверов в базе
                servers = self.sqlapi.get_servers()
                for server in servers:

                    host = server[0]
                    state = int(server[1])
                    error_count = int(server[2])
                    check_res = self.check_ping(host)

                    if (check_res != 0) and (state == 0):
                        print(datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S"), file=log)
                        print("Сервер ", host, " недоступен.",  file=log)
                        # Увеличить счетчик ошибок на 1 и обновить счетчик в базе данных
                        error_count += 1
                        self.sqlapi.update_error_count({"name": host, "error_count": error_count})
                    #
                    if (error_count >= count_of_check) and  (state == 0):
                        text = "Сервер " + host + " недоступен в течении " + str(self.interval * count_of_check) + " секунд"
                        print(datetime.datetime.now().strftime("%Y-%m-%d  %H-%M-%S"), file=log)
                        print(text, file=log)
                        self.mail.send(smtp_server, email_from, password_hash, email_from, email_to, "Сервер недоступен", text)
                        self.sqlapi.update_state({"name": host, "state": 1})

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
                if not self.error_mail:
                    print("Не вснесены все реквизиты в базу данных", file=log)
                    self.error_mail = True