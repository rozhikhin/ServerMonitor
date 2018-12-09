import winreg, ctypes, os, sys


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

    with open(log, 'a') as f:
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_key)
            winreg.SetValueEx(key, "DB_FILE", 0, winreg.REG_SZ, db)
            winreg.SetValueEx(key, "LOG_FILE", 0, winreg.REG_SZ, log)
            winreg.SetValueEx(key, "Service_exe", 0, winreg.REG_SZ, service_exe)
            winreg.CloseKey(key)
        except Exception as err:
            print(str(err), file=f)



def delete_reg_key():
        key = winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, reg_key)



def check_reg_key():
    try:
        winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key, 0, winreg.KEY_ALL_ACCESS)
        return True
    except Exception as err:
        # print(str(err), file = f)
        return False




def create_or_delete_reg_key():
    with open(log, 'a') as f:
            try:
                if check_reg_key():
                    delete_reg_key()
                else:
                    create_reg_key()
            except Exception as err:
                print(str(err), file=f)


# if is_admin():
create_or_delete_reg_key()
# else:
    # ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable,  os.path.abspath(__file__), None, 1)