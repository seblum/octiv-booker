import re

# Define the mapping of log levels to CSS classes and keywords
log_levels = {
    "user": ["USER:"],
    "info": ["|", "Possible classes:", "Switched to", "Time:"],
    "success": ["Login successful", "Booking", "OctivBooker succeeded"],
    "error": ["Error", "Could not identify Error", "Error message:"],
    "debug": ["Checking", "Start execution", "Executed", "Took"],
}


# Function to determine the log level and corresponding CSS class
def get_log_level_and_class(line):
    for level, keywords in log_levels.items():
        if any(keyword in line for keyword in keywords):
            return level
    return "info"


# Read the log file
with open("log.txt", "r") as file:
    lines = file.readlines()

# Create the HTML content
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

# Process each line in the log file
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

# Close the HTML tags
html_content += """
</table>

</body>
</html>
"""

# Write the HTML content to a file
with open("log.html", "w") as file:
    file.write(html_content)

print("HTML log report generated successfully.")
