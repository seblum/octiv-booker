import os
import sys
from datetime import datetime
import re

class LogHandler:
    def __init__(self):
        self.log_dir = "logs"
        self.log_file_path = None
        self.orig_stdout = sys.stdout

    def setup_log_dir(self) -> str:
        """
        Creates a directory for logs if it doesn't exist and generates a log file path based on the current date and time.

        Returns:
            str: Path to the generated log file.
        """
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        exact_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file_path = f"{self.log_dir}/log_{exact_datetime}.log"
        return self.log_file_path

    def start_logging(self) -> None:
        """Start logging by redirecting stdout to a log file.

        This function creates a log directory named 'logs' if it doesn't exist and sets up
        logging to a new log file with a filename containing the current date and time.

        Returns:
            None
        """
        self.setup_log_dir()
        self.file = open(self.log_file_path, "a+")
        sys.stdout = self.file
        print("-" * 5, datetime.now(), "-" * 5)
        print("\n<>")

    def stop_logging(self) -> None:
        """Stop logging and restore the original stdout.

        This function closes the log file and restores the original stdout so that subsequent
        print statements are displayed in the console as usual.

        Returns:
            None
        """
        print("<>")
        sys.stdout = self.orig_stdout
        self.file.close()

    def convert_logs_to_html(self) -> str:
        """
        Converts the log file to an HTML report.

        Returns:
            str
        """
        log_levels = {
            "user": ["USER:"],
            "info": ["|", "Possible classes:", "Switched to", "Time:"],
            "success": ["Login successful", "Booking", "OctivBooker succeeded"],
            "error": ["Error", "Could not identify Error", "Error message:"],
            "debug": ["Checking", "Start execution", "Executed", "Took"],
        }

        def get_log_level_and_class(line):
            for level, keywords in log_levels.items():
                if any(keyword in line for keyword in keywords):
                    return level
            return "info"

        with open(self.log_file_path, "r") as file:
            lines = file.readlines()

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
                log_class = get_log_level_and_class(message)
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
        html_file_name = self.log_file_path.replace(".log", ".html")
        with open(html_file_name, "w") as file:
            file.write(html_content)

        return self.log_file_path.replace(".log", ".html")
