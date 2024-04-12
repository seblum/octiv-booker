from email.message import EmailMessage
import re

log_content = """
2024-04-08 20:58:39,352 | submit user name successful
2024-04-08 20:58:40,962 | login successful
2024-04-08 20:58:46,329 | switched to following week
2024-04-08 20:58:47,720 | switched to day: Tuesday, 2024-04-16
2024-04-08 20:58:47,721 | Execution starts at >= 21:00:00
2024-04-08 20:58:48,883 ? possible classes for '['Open Gym', 'Remote Coaching']'
2024-04-08 20:58:49,030 - time: 06:00 - class: Open Gym
2024-04-08 20:58:49,151 - time: 07:30 - class: Open Gym
2024-04-08 20:58:49,223 - time: 09:00 - class: Open Gym
2024-04-08 20:58:49,296 - time: 13:00 - class: Open Gym
2024-04-08 20:58:49,345 - time: 15:00 - class: Open Gym
2024-04-08 20:58:49,394 - time: 16:00 - class: Remote Coaching
2024-04-08 20:58:49,443 - time: 16:00 - class: Open Gym
2024-04-08 20:58:49,517 - time: 17:30 - class: Open Gym
2024-04-08 20:58:49,581 - time: 17:30 - class: Remote Coaching
2024-04-08 20:58:49,670 - time: 19:00 - class: Open Gym
2024-04-08 20:58:49,737 - time: 19:00 - class: Remote Coaching
2024-04-08 20:58:49,865 - time: 20:30 - class: Open Gym
2024-04-08 20:58:49,915 - time: 20:30 - class: Remote Coaching
2024-04-08 20:58:49,915 ? Checking Open Gym at 19:00...
2024-04-08 20:58:49,915 | Booking Open Gym at 19:00
2024-04-08 21:00:00,000 | Executed at 21:00:00.000010
2024-04-08 21:00:03,090 | No Alert
2024-04-08 21:00:03,107 ! Error !
2024-04-08 21:00:03,133 ! Class is fully booked
2024-04-08 21:00:03,134 ? Checking Remote Coaching at 19:00...
2024-04-08 21:00:03,134 | Booking Remote Coaching at 19:00
2024-04-08 21:00:03,149 | Executed at 21:00:03.149674
2024-04-08 21:00:06,201 | No Alert
2024-04-08 21:00:06,213 ! Error !
2024-04-08 21:00:06,234 ! Class is fully booked
2024-04-08 21:00:06,235 ? Checking Open Gym at 20:30...
2024-04-08 21:00:06,235 | Booking Open Gym at 20:30
2024-04-08 21:00:06,249 | Executed at 21:00:06.249719
2024-04-08 21:00:09,309 | No Alert
2024-04-08 21:00:09,320 ! Error !
2024-04-08 21:00:09,341 ! Class is fully booked
2024-04-08 21:00:09,427 | [1] OctivBooker succeeded
"""

# Splitting the log content into individual lines
log_lines = log_content.strip().split('\n')

# Regular expressions for different log entry types
regex_datetime = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')
regex_info = re.compile(r'\| (.+)')
regex_warning = re.compile(r'! (.+)')
regex_error = re.compile(r'\? (.+)')

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
print(html_content)