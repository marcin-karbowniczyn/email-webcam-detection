import smtplib
import imghdr  # This library gives us metadata about images
from os import getenv
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()


def send_email(image_path):
    email_message = EmailMessage()
    email_message['Subject'] = 'New camera detection'
    # Email body
    email_message.set_content('Hey, someone has beed detected by the camera.')

    # Read binary, for the image
    with open(image_path, 'rb') as file:
        content = file.read()
    # mghdr.what() this method will fine out what kind of image is in the content
    email_message.add_attachment(content, maintype='image', subtype=imghdr.what(None, content))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(getenv('GMAIL_SENDE'), getenv('GMAIL_PASSWORD'))
        server.sendmail(getenv('GMAIL_SENDER'), getenv('EMAIL_RECIEVER'), email_message.as_string())

    # THE WAY WE WOULD DO IT WITOUT WITH CONTEXT MANAGER
    # gmail = smtplib.SMTP('smtp.gmail.com', 587)
    # gmail.ehlo()
    # gmail.starttls()
    # gmail.login(sender, password)
    # gmail.sendmail(sender, reciever, email_message.as_string())
    # gmail.quit()


if __name__ == '__main__':
    send_email(image_path='images/19.png')
