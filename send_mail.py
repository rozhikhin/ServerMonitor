import smtplib
from cryptography.fernet import Fernet
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class RAMail():
    def __init__(self):
        self.ra_key = b'Aaytm4yaA5C_mAG_IOzWeF5P4wR204Wk57QEqqDDKTA='
        self.cipher = Fernet(self.ra_key)

    def send(self, host, username, password_hash, mail_from, mail_to, subject, text, port = 25, tls = 0):
        password = self.decode_password(password_hash)
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
        server.sendmail(mail_from, mail_to, msg.as_string())
        server.quit()

    def encode_password(self, password):
        password = password.encode()
        encrypted_text = self.cipher.encrypt(password)
        return encrypted_text

    def decode_password(self, password_hash):
        if password_hash:
            decrypted_text = self.cipher.decrypt(password_hash).decode()
            return decrypted_text
        else:
            return ""

