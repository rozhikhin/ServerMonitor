import smtplib

class RAMail():
    def __init__(self, host, username, password, mail_from, mail_to, subject, body, port = 25, tls = False,):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.mail_from = mail_from
        self.mail_to = mail_to
        self.subject = subject
        self.body = body
        self.tls = tls

    def send(self):
        server = smtplib.SMTP(self.host, self.port)
        server.login(self.username, self.password)
        if self.tls:
            server.starttls()
        server.sendmail(self.mail_from, self.mail_to, self.body)
        server.quit()

    def encode_password(self, password):
        pass

    def decode_password(self, hash):
        pass

HOST = "mail.alpha-medica.ru"
SUBJECT = "Test email from Python"
TO = "a@alpha-medica.ru"
FROM = "admin@a.ru"
text = "Python 3.4 rules them all!"
username = "admin@a.ru"
password = "1111"

BODY = "\r\n".join((
    "From: %s" % FROM,
    "To: %s" % TO,
    "Subject: %s" % SUBJECT,
    "",
    text
))

sm = RAMail(HOST, username, password, FROM, TO, SUBJECT, BODY)
sm.send()
