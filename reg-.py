import winreg, ctypes, os


reg_key = r'Software\Rozhikhin\ServerMonitor'
db =  os.path.join(os.getcwd(), "monitor.db")
log =  os.path.join(os.getcwd(), "monitor.log")
service_exe = os.path.join(os.getcwd(), "server_monitor_service.exe")



def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def create_reg_key():
    if is_admin():
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key, 0, winreg.KEY_ALL_ACCESS)
        except:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_key)
        winreg.SetValueEx(key, "DB_FILE", 0, winreg.REG_SZ, db)
        winreg.SetValueEx(key, "LOG_FILE", 0, winreg.REG_SZ, log)
        winreg.SetValueEx(key, "Service_exe", 0, winreg.REG_SZ, service_exe)
        winreg.CloseKey(key)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', 'python.exe', os.path.abspath(__file__),
                                        None, 1)


def delete_reg_key():
    with open(log, 'a') as f:
        if is_admin():
            try:
                key = winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, reg_key, 0, winreg.KEY_ALL_ACCESS)
            except Exception as err:
                print(str(err), file = f)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, 'runas', 'python.exe', os.path.abspath(__file__),
                                            None, 1)


def check_reg_key():
    with open(log, 'a') as f:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key, 0, winreg.KEY_ALL_ACCESS)
            return True
        except Exception as err:
            print(str(err), file = f)
            return False


print(log)

if check_reg_key():
    delete_reg_key()
else:
    create_reg_key()
