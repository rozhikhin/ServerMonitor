"""
Модуль содержит класс для работы с электронной почтой
"""
import smtplib
from cryptography.fernet import Fernet
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class RAMail():
    """
    Класс RAMail содержит функции отправки почты и функции для шифрования-дешифрования пароля
    """
    def __init__(self):
        # Ключ для расшифровки и шифрования пароля
        self.ra_key = b'Aaytm4yaA5C_mAG_IOzWeF5P4wR204Wk57QEqqDDKTA='
        self.cipher = Fernet(self.ra_key)

    def send(self, host, username, password_hash, mail_from, mail_to, subject, text, port = 25, tls = 0):
        """
        Метод send отправляет сообщение
        :param host: str
        :param username: str
        :param password_hash: str
        :param mail_from: str
        :param mail_to: str
        :param subject: str
        :param text: str
        :param port: int
        :param tls: int
        :return: None
        """

        # Расшифровываем пароль
        password = self.decode_password(password_hash)
        # Подготавливаем сообщение
        msg = MIMEMultipart()
        msg["Subject"] = Header(subject, 'utf-8')
        msg["From"] = Header(mail_from, 'utf-8')
        msg["To"] = Header(mail_to, 'utf-8')
        text = MIMEText(('<br><h3>' + text  + '</h3>').encode('utf-8'), 'html', _charset='utf-8')
        msg.attach(text)

        server = smtplib.SMTP(host, port)
        server.login(username, password)
        if tls == 1:
            server.starttls()
        # Отправляем сообщение
        server.sendmail(mail_from, mail_to, msg.as_string())
        server.quit()

    def encode_password(self, password):
        """
        Метод encode_password шифрует пароль
        :param password: str
        :return: encrypted_text: str
        """
        password = password.encode()
        encrypted_text = self.cipher.encrypt(password)
        return encrypted_text

    def decode_password(self, password_hash):
        """
        Метод encode_password расшифровывает пароль
        :param password_hash: str
        :return: decrypted_text: str
        """
        if password_hash:
            decrypted_text = self.cipher.decrypt(password_hash).decode()
            return decrypted_text
        else:
            return ""

