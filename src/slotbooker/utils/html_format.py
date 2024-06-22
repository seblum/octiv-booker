import re


def format_to_html(body) -> str:
    log_content = body

    # Splitting the log content into individual lines
    log_lines = log_content.strip().split("\n")

    # Regular expressions for different log entry types
    regex_datetime = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})")
    regex_info = re.compile(r"\| (.+)")
    regex_warning = re.compile(r"! (.+)")
    regex_error = re.compile(r"\? (.+)")

    # HTML table template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    table {{
    font-family: Arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    }}

    td, th {{
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
    }}

    th {{
    background-color: #f2f2f2;
    }}
    </style>
    </head>
    <body>

    <h2>Log Entries</h2>

    <table>
    <tr>
        <th>Timestamp</th>
        <th>Type</th>
        <th>Message</th>
    </tr>
    {}
    </table>

    </body>
    </html>
    """

    # Initialize HTML rows
    html_rows = ""

    # Convert each log line to HTML row
    for line in log_lines:
        timestamp_match = regex_datetime.match(line)
        info_match = regex_info.search(line)
        warning_match = regex_warning.search(line)
        error_match = regex_error.search(line)
        
        if timestamp_match:
            timestamp = timestamp_match.group(1)
            
            if info_match:
                log_type = "Info"
                message = info_match.group(1)
            elif warning_match:
                log_type = "Warning"
                message = warning_match.group(1)
            elif error_match:
                log_type = "Error"
                message = error_match.group(1)
            else:
                log_type = "Unknown"
                message = ""
            
            html_rows += f"<tr><td>{timestamp}</td><td>{log_type}</td><td>{message}</td></tr>"

    # Complete HTML content
    html_content = html_template.format(html_rows)

    # Print or use html_content as needed
    return html_content
