import os
import sys
from datetime import datetime
import re
from email.message import EmailMessage
import ssl
import smtplib
from typing import Dict, List, Tuple

LOG_DIR = "logs"
LOG_FILE_TEMPLATE = "log_{timestamp}.log"
HTML_FILE_TEMPLATE = "log_{timestamp}.html"
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 465
LOG_LEVELS: Dict[str, List[str]] = {
    "user": ["USER:"],
    "info": ["|", "Possible classes:", "Switched to", "Time:"],
    "success": ["Login successful", "Booking", "OctivBooker succeeded"],
    "error": ["Error", "Could not identify Error", "Error message:"],
    "debug": ["Checking", "Start execution", "Executed", "Took"],
}

class LogHandler:
    def __init__(self) -> None:
        self.log_dir = LOG_DIR
        self.log_file_path: str = ""
        self.orig_stdout = sys.stdout

    def setup_log_dir(self) -> str:
        """
        Creates a directory for logs if it doesn't exist and generates a log file path based on the current date and time.

        Returns:
            str: Path to the generated log file.
        """
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file_path = os.path.join(self.log_dir, LOG_FILE_TEMPLATE.format(timestamp=timestamp))
        return self.log_file_path

    def start_logging(self) -> None:
        """Start logging by redirecting stdout to a log file."""
        self.setup_log_dir()
        self.file = open(self.log_file_path, "a+")
        sys.stdout = self.file
        print(f"----- {datetime.now()} -----")
        print("\n<>")

    def stop_logging(self) -> None:
        """Stop logging and restore the original stdout."""
        print("<>")
        sys.stdout = self.orig_stdout
        self.file.close()

    def convert_logs_to_html(self) -> str:
        """
        Converts the log file to an HTML report.

        Returns:
            str: Path to the generated HTML file.
        """
        with open(self.log_file_path, "r") as file:
            lines = file.readlines()

        html_content = self._generate_html_content(lines)
        html_file_path = self.log_file_path.replace(".log", ".html")

        with open(html_file_path, "w") as file:
            file.write(html_content)

        return html_file_path

    def _generate_html_content(self, lines: List[str]) -> str:
        """
        Generates HTML content from log lines.

        Args:
            lines (List[str]): List of log lines.

        Returns:
            str: Generated HTML content.
        """
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                .log-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .log-table th, .log-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                }
                .log-table th {
                    background-color: #f2f2f2;
                    text-align: left;
                }
                .user {
                    font-weight: bold;
                }
                .info {
                    color: blue;
                }
                .success {
                    color: green;
                }
                .warning {
                    color: orange;
                }
                .error {
                    color: red;
                }
                .debug {
                    color: purple;
                }
            </style>
        </head>
        <body>
        <h2>Log Report</h2>
        <table class="log-table">
            <tr>
                <th>Timestamp</th>
                <th>Message</th>
            </tr>
        """
        for line in lines:
            match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})(.*)", line)
            if match:
                timestamp, message = match.groups()
                log_class = self._get_log_level_and_class(message)
                html_content += f"""
                <tr>
                    <td>{timestamp.strip()}</td>
                    <td class="{log_class}">{message.strip()}</td>
                </tr>
                """
        html_content += """
        </table>
        </body>
        </html>
        """
        return html_content

    def _get_log_level_and_class(self, message: str) -> str:
        """
        Determines the log level and corresponding CSS class for a log message.

        Args:
            message (str): The log message.

        Returns:
            str: The CSS class corresponding to the log level.
        """
        for level, keywords in LOG_LEVELS.items():
            if any(keyword in message for keyword in keywords):
                return level
        return "info"

    def send_logs_to_mail(self, filename: str, response: str, format: str = "plain") -> None:
        """
        Send an email with the content of the specified file as the email body.

        Args:
            filename (str): The name of the file whose content will be used as the email body.
            response (str): The response status to be included in the email subject.
            format (str): The format of the email body (default is "plain").

        Raises:
            OSError: If the specified file cannot be opened or read.
        """
        email_sender = os.getenv("EMAIL_SENDER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_receiver = os.getenv("EMAIL_RECEIVER")

        if not all([email_sender, email_password, email_receiver]):
            raise ValueError("Email sender, password, and receiver must be set as environment variables")

        email_receiver_list = email_receiver.split(";")
        subject = f"[{response}] OctivBooker report"

        with open(filename, "r") as file:
            body = file.read()

        self._send_email(email_sender, email_password, email_receiver_list, subject, body, format)

    def _send_email(self, sender: str, password: str, receivers: List[str], subject: str, body: str, format: str) -> None:
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
        em.set_content(body, format)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, context=context) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receivers, em.as_string())

        print("email_sent")
