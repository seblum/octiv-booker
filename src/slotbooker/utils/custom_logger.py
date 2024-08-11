import os
import sys
from datetime import datetime
import logging
import re
from typing import Dict, List

# Constants for logging configuration
LOG_DIR = "logs"
LOG_FILE_TEMPLATE = "log_{timestamp}.log"

LOG_LEVELS: Dict[str, str] = {
    "INFO": "info",
    "DEBUG": "debug",
    "WARNING": "warning",
    "ERROR": "error",
    "SUCCESS": "success",
    "USER": "user",
}


class LogHandler:
    def __init__(self) -> None:
        self.timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_dir = LOG_DIR
        self.log_file_path: str = self._setup_log_dir()
        self.orig_stdout = sys.stdout

        # Set up custom logger
        logging.setLoggerClass(CustomLogger)
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(
            filename=self.log_file_path,
            filemode="w",
            encoding="utf-8",
            format="%(asctime)s %(levelname)s %(message)s",
            level=logging.INFO,
        )

    def get_log_file_path(self) -> str:
        return self.log_file_path

    def _setup_log_dir(self) -> str:
        """
        Creates a directory for logs if it doesn't exist and generates a log file path based on the current date and time.

        Returns:
            str: Path to the generated log file.
        """
        os.makedirs(self.log_dir, exist_ok=True)
        return os.path.join(
            self.log_dir, LOG_FILE_TEMPLATE.format(timestamp=self.timestamp)
        )

    def start_logging(self) -> None:
        """Start logging by redirecting stdout to a log file."""
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
            match = re.match(
                r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+) (.*)", line
            )
            if match:
                timestamp, log_level, message = match.groups()
                log_class = LOG_LEVELS.get(log_level, "info")
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


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        # Define the custom log level
        self.SUCCESS = 25
        logging.addLevelName(self.SUCCESS, "SUCCESS")

        logging.success = self.success
        logging.Logger.success = self.success

    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(self.SUCCESS):
            self._log(self.SUCCESS, message, args, **kwargs)
