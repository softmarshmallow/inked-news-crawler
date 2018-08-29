import smtplib
from email.mime.multipart import MIMEMultipart
import sys
from email.mime.text import MIMEText


def send_email(title, extra=""):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    #Next, log in to the server
    server.login("softmarshmallow.dummy@gmail.com", "DUMMY@password")

    msg = MIMEMultipart()
    msg['From'] = 'softmarshmallow.dummy@gmail.com'
    msg['To'] = 'woojoo@softmarshmallow.com'
    msg['Subject'] = title
    try:
        err = str(sys.last_value)
    except AttributeError:
        err = "No error"
    body = """
    process complete
    check info below. it may contain debug info.
    
    Err: %s
    Exceptions: %s
    """ % (err, extra)
    body = MIMEText(body)
    msg.attach(body)


    #Send the mail
    server.sendmail("softmarshmallow.dummy@gmail.com", "woojoo@softmarshmallow.com", msg.as_string())
    server.quit()
