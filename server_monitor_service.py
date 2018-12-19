"Модуль содержит класс для создания службы Windows"
import servicemanager
import socket
import sys
import win32event
import win32service
import win32serviceutil
from servers_check import Ping



class ServerMonitorService(win32serviceutil.ServiceFramework):
    "Модуль содержит класс для создания службы Windows"
    _svc_name_ = "server_monitor"
    _svc_display_name_ = "Server monitor service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        # Запуск целевого метода
        self.ping = Ping()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            self.ping.run()
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.ping.interval * 1000)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ServerMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ServerMonitorService)

