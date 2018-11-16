""" Модуль содержит класс для работы с базой данных """
import sqlite3
import os
from tkinter import messagebox


class DB():
    """
    Класс DB содержит содержит набор функций для создани БД SQLite и для работы с ней.
    Также содержит словарь для заполнения БД данными по-умолчанию.
    """
    def __init__(self):
        """
        Конструктор инициализирует словарь для сохранения в БД значений по-умолчанию
        """
        self.db_file = os.path.join(os.getcwd(), "monitor.db")

        # Настройки по-умолчанию общие
        self.settings = {
            "id_setting": 1,
            "interval": 60,
            "count_of_check": 10,
            "email_from": ""
        }

    def init_db(self):
        """
        Функция init_db() создает базу данных и заполняет ее значениями по-умолчанию.
        Для этого она использует следующие функции класса DB:
            - create_db() - создает базу в случае ее отсутствия
            - self.check_default_settings() -  проверяет, есть ли в таблице setting запись с ID=1
            - set_default_settings() - если предыдущая функция вернула количество записей 0 -
            заполняет таблицы значениями по-умолчанию.
        """
        self.create_db()
        col_rows = self.check_default_settings()
        if col_rows == 0:
            self.set_default_settings()

    def create_connection(self):
        """
        Функция create_connection() создает базу данных и возращает объект подключения к БД.
        """

        try:
            con = sqlite3.connect(self.db_file)
            con.execute('pragma journal_mode=off')
            # con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
        except sqlite3.Error as error:
            messagebox.showerror("Ошибка базы данных", str(error))
            return error
        return con

    def create_db(self):
        """
        Функция create_db() создает таблицы базы данных
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        sql = """\
            CREATE TABLE IF NOT EXISTS setting (
                id_setting INTEGER PRIMARY KEY AUTOINCREMENT,
                interval INTEGER default 60,
                count_of_check INTEGER default 10,
                email_from  TEXT default "",
                email_to  TEXT default "",
                password_hash TEXT default "",
                smtp_server TEXT default "",
                smtp_port INTEGER default 25,
                start_tls INTEGER default 0
                );

            CREATE TABLE IF NOT EXISTS servers (
                server_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                state TEXT NOT NULL default "OK",
                error_count INTEGER default 0
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_servers_name ON servers (name);
            """

        try:
            cursor.executescript(sql)
        except sqlite3.DatabaseError as error:
            return self.show_db_error(error)

    def check_default_settings(self):
        """
        Функция check_default_settings() делает запрос к базе данных и проверяет, есть ли в таблице setting
        запись с ID=1
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql = "SELECT count(*) FROM setting WHERE id_setting=1"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0]
        except sqlite3.DatabaseError as error:
            return self.show_db_error(error)

    def set_default_settings(self):
        """
        Функция set_default_settings() заполняет таблицы значениями по-умолчанию при инициализации приложения
        и при сбросе настроек
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql_settings = """INSERT INTO setting (id_setting, interval, count_of_check, email_from) 
                        VALUES (:id_setting, :interval, :count_of_check, :email_from)"""
            cursor.execute(sql_settings, self.settings)
            connection.commit()
        except sqlite3.DatabaseError as error:
            return self.show_db_error(error)

    # def reset_to_default_settings(self):
    #     """
    #     Функция reset_to_default_settings() возвращает записи в таблицах к значениям по-умолчанию
    #     """
    #     connection = self.create_connection()
    #     cursor = connection.cursor()
    #     try:
    #         sql_settings = """UPDATE setting SET interval=:interval, count_of_check=:count_of_check, email=:email                
    #                     WHERE id_setting=:id_setting"""
    #         sql_server_list= """DELETE FROM servers"""
    #         cursor.execute(sql_settings, self.settings)
    #         cursor.execute(sql_server_list, self.font)
    #         connection.commit()
    #     except sqlite3.DatabaseError as error:
    #         return self.show_db_error(error)

    # Получить парамнтры из базы данных
    def get_settings(self):
        """
        Функция get_settings() делает выборку из таблицы setting
        :return:  кортеж - выборка из бд
        """
        try:
            con = self.create_connection()
            cursor = con.cursor()
            sql_settings = "SELECT interval, count_of_check, email_from FROM setting"
            cursor.execute(sql_settings)
            return cursor.fetchone()
        except sqlite3.DatabaseError as error:
            return self.show_db_error(error)

    # Получить список серверов из базы данных
    def get_servers(self):
        """
        Функция get_servers() делает выборку севреров из таблицы servers
        :return:  List - выборка из бд
        """
        con = self.create_connection()
        cursor = con.cursor()
        try:
            sql_srver_list= "SELECT name, state, error_count FROM servers"
            cursor.execute(sql_srver_list)
            return cursor.fetchall()
        except sqlite3.DatabaseError as error:
            return self.show_db_error(error)

    # Получить список серверов из базы данных
    def get_servers_name_and_state(self):
        """
        Функция get_servers() делает выборку севреров из таблицы servers
        :return:  List - выборка из бд
        """
        con = self.create_connection()
        cursor = con.cursor()
        try:
            sql_srver_list= "SELECT name, state FROM servers"
            cursor.execute(sql_srver_list)
            return cursor.fetchall()
        except sqlite3.DatabaseError as error:
            return self.show_db_error(error)



    def update_error_count(self, data):
        """
        Функция update_error_count(error_count) обновляет счетчик ошибок в БД
        :param data:
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql_str = """UPDATE servers SET error_count=:error_count WHERE name=:name"""
            cursor.execute(sql_str, data)
            connection.commit()
        except sqlite3.DatabaseError as error:
            self.show_db_error(error)

    def update_state(self, data):
        """
        Функция update_state() устанавливает ( state == ERROR ) или снимает ( state == OK ) состояние сервера в БД
        :param data:
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql_str = """UPDATE servers SET state=:state WHERE name=:name"""
            cursor.execute(sql_str, data)
            connection.commit()
        except sqlite3.DatabaseError as error:
            self.show_db_error(error)

    def update_settings(self, changed_settings):
        """
        Функция update_settings(changed_settings) обновляет данные в БД
        :param changed_settings:
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql_settings = """UPDATE setting SET interval=:interval, count_of_check=:count_of_check,             
                    email_from=:email_from, email_to=:email_to, password_hash=:password, smtp_server=:smtp_server,
                    smtp_port=:smtp_port, start_tls=:tls
                    WHERE id_setting=1"""
            cursor.execute(sql_settings, changed_settings)
            connection.commit()
        except sqlite3.DatabaseError as error:
            self.show_db_error(error)
            
    def save_server(self, server_data):
        """
        Функция save_server сохраняет новую запись сервера в базе данных
        :param server_data: dict
        :return: bool
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql_server = """INSERT INTO servers(name, state) VALUES (:server_name, :state)"""
            cursor.execute(sql_server, server_data)
            connection.commit()
            return True
        except sqlite3.DatabaseError as error:
            self.show_db_error(error)
            return False

    def update_server(self, server_data):
        """
        Функция update_server сохраняет отредактированную запись сервера в базе данных
        :param server_data: dict
        :return: bool
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql_settings = """UPDATE servers SET name=:server_name, state=:state WHERE name=:old_name"""
            cursor.execute(sql_settings, server_data)
            connection.commit()
            return True
        except sqlite3.DatabaseError as error:
            self.show_db_error(error)
            return False
        
    def delete_server(self, server_data):
        """
        Функция delete_server сохраняет отредактированную запись сервера в базе данных
        :param server_data: dict
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            sql_server = """DELETE FROM servers WHERE name=:server_name"""
            cursor.execute(sql_server, server_data)
            connection.commit()
        except sqlite3.DatabaseError as error:
            self.show_db_error(error)

    def show_db_error(self, error):
        """
        Функция show_db_error(error) выводит окно с сообщением об ошибке при работе с базой данных
        :param error:
        :return: None
        """
        if 'UNIQUE constraint' in str(error):
            messagebox.showerror("Ошибка базы данных", "Имя уже существеут")
            return
        messagebox.showerror("Ошибка базы данных", str(error))




