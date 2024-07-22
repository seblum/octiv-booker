import os
from email.message import EmailMessage
import ssl
import smtplib
from typing import List
from datetime import datetime
from string import Template

EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 465


class MailHandler:
    html_templates_path = "html/"

    def __init__(self, format: str = "plain") -> None:
        self.format = format
        self.email_sender = None
        self.email_password = None
        self.email_receiver = None

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

        if not all([self.email_sender, self.email_password, self.email_receiver]):
            raise ValueError(
                "Email sender, password, and receiver must be set as environment variables"
            )

        email_receiver_list = self.email_receiver.split(";")
        subject = f"[{response}] OctivBooker report"

        with open(filename, "r") as file:
            body = file.read()

        self._send_email(
            sender=self.email_sender,
            password=self.email_password,
            receivers=email_receiver_list,
            subject=subject,
            body=body,
        )

    def _send_email(
        self,
        sender: str,
        password: str,
        receivers: List[str],
        subject: str,
        body: str,
        attachment_path: str = None,
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
            attachment_path (str): The path to the file to be attached (default is None).
        """
        em = EmailMessage()
        em["From"] = sender
        em["To"] = ", ".join(receivers)
        em["Subject"] = subject
        em.set_content(body, self.format)

        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                file_data = attachment.read()
                file_name = os.path.basename(attachment_path)
                em.add_attachment(
                    file_data,
                    maintype="text",
                    subtype="plain",
                    filename=file_name,
                )

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, context=context
        ) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receivers, em.as_string())

        print("Email sent successfully!")

    def send_successful_booking_email(
        self,
        booking_date: str,
        booking_time: str,
        booking_name: str,
        attachment_path: str = None,
    ) -> None:
        """
        Send a beautifully formatted HTML email announcing a successful booking.

        Args:
            booking_time (str): The time of the booking.
            booking_name (str): The name of the booking.
            receiver_name (str): The name of the receiver.
        """
        email_receiver_name = os.getenv("EMAIL_RECEIVER_NAME")

        if not all([self.email_sender, self.email_password, self.email_receiver]):
            raise ValueError("Email sender, password, and receiver email must be set.")

        if email_receiver_name is None:
            email_receiver_name = self.email_receiver.split("@")[0]

        subject = "Booking Confirmation"

        # Get the current working directory and construct the file path
        current_path = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(
            current_path, f"{self.html_templates_path}template_successful_booking.html"
        )

        # Read the HTML template from the file
        with open(template_path, "r") as file:
            template = Template(file.read())

        # Customize the template with actual values
        body = template.safe_substitute(
            receiver_name=email_receiver_name,
            booking_name=booking_name,
            booking_time=booking_time,
            booking_date=booking_date,
            current_year=datetime.now().year,
        )

        self._send_email(
            sender=self.email_sender,
            password=self.email_password,
            receivers=[self.email_receiver],
            subject=subject,
            body=body,
            attachment_path=attachment_path,
        )

    def send_unsuccessful_booking_email(
        self,
        booking_date: str,
        booking_time: str,
        booking_name: str,
        attachment_path: str = None,
    ) -> None:
        """
        Send a beautifully formatted HTML email announcing an unsuccessful booking.

        Args:
            receiver_name (str): The name of the receiver.
            attachment_path (str): The path to the file to be attached (default is None).
        """
        email_receiver_name = os.getenv("EMAIL_RECEIVER_NAME")

        if not all([self.email_sender, self.email_password, self.email_receiver]):
            raise ValueError("Email sender, password, and receiver email must be set.")

        if email_receiver_name is None:
            email_receiver_name = self.email_receiver.split("@")[0]

        subject = "Booking Not Successful"

        # Get the current working directory and construct the file path
        current_path = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(
            current_path,
            f"{self.html_templates_path}template_unsuccessful_booking.html",
        )

        # Read the HTML template from the file
        with open(template_path, "r") as file:
            template = Template(file.read())

        # Customize the template with actual values
        body = template.safe_substitute(
            receiver_name=email_receiver_name,
            booking_name=booking_name,
            booking_time=booking_time,
            booking_date=booking_date,
            current_year=datetime.now().year,
        )

        self._send_email(
            sender=self.email_sender,
            password=self.email_password,
            receivers=[self.email_receiver],
            subject=subject,
            body=body,
            attachment_path=attachment_path,
        )

    def send_no_classes_email(
        self, booking_date: str, attachment_path: str = None
    ) -> None:
        """
        Send a beautifully formatted HTML email announcing that no classes were found.

        Args:
            receiver_name (str): The name of the receiver.
            attachment_path (str): The path to the file to be attached (default is None).
        """
        email_receiver_name = os.getenv("EMAIL_RECEIVER_NAME")

        if not all([self.email_sender, self.email_password, self.email_receiver]):
            raise ValueError("Email sender, password, and receiver email must be set.")

        if email_receiver_name is None:
            email_receiver_name = self.email_receiver.split("@")[0]

        subject = "No Classes Found"

        # Get the current working directory and construct the file path
        current_path = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(
            current_path, f"{self.html_templates_path}template_neutral_booking.html"
        )

        # Read the HTML template from the file
        with open(template_path, "r") as file:
            template = Template(file.read())

        # Customize the template with actual values
        body = template.safe_substitute(
            receiver_name=email_receiver_name,
            booking_date=booking_date,
            current_year=datetime.now().year,
        )

        self._send_email(
            sender=self.email_sender,
            password=self.email_password,
            receivers=[self.email_receiver],
            subject=subject,
            body=body,
            attachment_path=attachment_path,
        )
