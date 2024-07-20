import os
from email.message import EmailMessage
import ssl
import smtplib
from typing import List
from datetime import datetime

EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 465


class MailHandler:
    def __init__(self, format: str = "plain") -> None:
        self.format = format

    def send_logs_to_mail(
        self,
        filename: str,
        response: str,
    ) -> None:
        """
        Send an email with the content of the specified file as the email body.

        Args:
            filename (str): The name of the file whose content will be used as the email body.
            response (str): The response status to be included in the email subject.

        Raises:
            OSError: If the specified file cannot be opened or read.
        """
        email_sender = os.getenv("EMAIL_SENDER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_receiver = os.getenv("EMAIL_RECEIVER")

        if not all([email_sender, email_password, email_receiver]):
            raise ValueError(
                "Email sender, password, and receiver must be set as environment variables"
            )

        email_receiver_list = email_receiver.split(";")
        subject = f"[{response}] OctivBooker report"

        with open(filename, "r") as file:
            body = file.read()

        self._send_email(
            email_sender,
            email_password,
            email_receiver_list,
            subject,
            body,
            self.format,
        )

    def _send_email(
        self,
        sender: str,
        password: str,
        receivers: List[str],
        subject: str,
        body: str,
    ) -> None:
        """
        Sends an email with the specified parameters.

        Args:
            sender (str): The email address of the sender.
            password (str): The password of the sender's email account.
            receivers (List[str]): A list of receiver email addresses.
            subject (str): The subject of the email.
            body (str): The body of the email.
            format (str): The format of the email body.

        """
        em = EmailMessage()
        em["From"] = sender
        em["To"] = ", ".join(receivers)
        em["Subject"] = subject
        em.set_content(body, self.format)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, context=context
        ) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receivers, em.as_string())

        print("email_sent")

    def send_successful_booking_email(
        self, booking_time: str, booking_name: str, receiver_name: str
    ) -> None:
        """
        Send a beautifully formatted HTML email announcing a successful booking.

        Args:
            booking_time (str): The time of the booking.
            booking_name (str): The name of the booking.
            receiver_name (str): The name of the receiver.
            receiver_email (str): The email address of the receiver.
        """
        email_sender = os.getenv("EMAIL_SENDER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_receiver = os.getenv("EMAIL_RECEIVER")

        if not all([email_sender, email_password, email_receiver]):
            raise ValueError("Email sender, password, and receiver email must be set.")

        subject = "Booking Confirmation"
        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 0;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    padding: 20px;
                    text-align: center;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #888888;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Dear {receiver_name},</p>
                    <p>We are pleased to inform you that your booking for <strong>{booking_name}</strong> has been successfully confirmed.</p>
                    <p><strong>Booking Time:</strong> {booking_time}</p>
                    <p>Thank you for choosing our service. We look forward to seeing you!</p>
                    <p>Best Regards,</p>
                    <p><strong>Your Company Name</strong></p>
                </div>
                <div class="footer">
                    <p>If you have any questions, please contact us at support@yourcompany.com</p>
                    <p>&copy; {datetime.now().year} Your Company Name. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = subject
        em.set_content(body, subtype="html")

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, context=context
        ) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

        print("Email sent successfully!")
