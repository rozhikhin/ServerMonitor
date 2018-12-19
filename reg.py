"""
Модуль с функциями создания и удаления записей в реестре
"""
import winreg, ctypes, os

# Ключ реестра, в котором будут храгиться записи
reg_key = r'Software\Rozhikhin\ServerMonitor'
# Путь к базе данных
db =  os.path.join(os.getcwd(), "monitor.db")
# Путь к лог-файлу
log =  os.path.join(os.getcwd(), "monitor.log")
# Путь к исполняемому файлу службы
service_exe = os.path.join(os.getcwd(), "server_monitor_service.exe")


def create_reg_key():
    """
    Функция create_reg_key создает необходимые записи в реестре (при регистрации службы)
    :return: None
    """
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
    """
    Функция delete_reg_key удаляет записи в реестре (при удалении службы)
    :return: None
    """
    key = winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, reg_key)

def check_reg_key():
    """
    Функция check_reg проверяет - существует ли ключ в реестре
    :return: boolean
    """
    try:
        winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key, 0, winreg.KEY_ALL_ACCESS)
        return True
    except Exception as err:
        return False

def create_or_delete_reg_key():
    """
    В зависимости от того, существует ли ключ реестра, функция create_or_delete_reg_key вызывает соответсвующую
    функцию удаления или создания записей реестра
    :return: None
    """
    with open(log, 'a') as f:
            try:
                if check_reg_key():
                    delete_reg_key()
                else:
                    create_reg_key()
            except Exception as err:
                print(str(err), file=f)

create_or_delete_reg_key()
