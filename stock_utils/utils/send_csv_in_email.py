from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "465"
SMTP_USERNAME = "pennies4v@gmail.com"
SMTP_PASSWORD = "mfoxdpakyqsqezqk"
def send_mail( subject, to, body="Sending Email from vishal_private_server", file_name =""):
    # Create a multipart message
    msg = MIMEMultipart()
    body_part = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = SMTP_USERNAME
    msg['To'] = to
    # Add body to email
    msg.attach(body_part)
    # open and read the CSV file in binary
    if file_name:
        with open(file_name,'rb') as file:
        # Attach the file with filename to the email
            msg.attach(MIMEApplication(file.read(), Name=file_name))
    

    # server = smtplib.SMTP(SMTP_SERVER, 587)
    server = smtplib.SMTP_SSL(SMTP_SERVER)
    server.connect(SMTP_SERVER,465)
    server.ehlo()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SMTP_USERNAME, to, text)
    server.quit()

# send_mail(r"C:\Users\vpa20\Documents\PythonCodes\high_rsi_file_230616154828.csv","High RSI Stock", "vishal.pathak86@gmail.com")