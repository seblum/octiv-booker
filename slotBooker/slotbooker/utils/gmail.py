# smwtrkqslxmkzhpu
import os
from email.message import EmailMessage
import ssl
import smtplib
from .html_format import format_to_html

def send_logs_to_mail(filename: str) -> None:
    """Send an email with the content of the specified file as the email body.

    Args:
        filename (str): The name of the file whose content will be used as the email body.

    Returns:
        None: This function does not return anything. It sends the email and prints a confirmation message.

    Raises:
        OSError: If the specified file cannot be opened or read.

    Note:
        - The email sender, password, and receiver must be set as environment variables:
          EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER.
        - The email will be sent using SMTP with SSL, specifically using Gmail's SMTP server.

    Example:
        To use this function, make sure you have set the required environment variables
        (EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER) and call the function with the filename:

        >>> send_logs_to_mail("report.txt")
    """
    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_receiver = os.getenv("EMAIL_RECEIVER")

    # read email body from logs
    subject = "OctivBooker report"
    with open(filename) as fp:
        body = fp.read()

    # body = format_to_html(body)
        
    # build email
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(body, "plain")

    context = ssl.create_default_context()

    # send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    print("email_sent")
