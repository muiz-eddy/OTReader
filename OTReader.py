# This script will filter your logs 
# if it is more than 18:00 then it will output all your logs before that on that day
# and also count in on the weekends

import datetime

# Open the git log file
with open(input("Path to your input file (only txt for now): "), 'r') as file:
    lines = file.readlines()

# Helper function to parse datetime
def parse_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")

# Find all weekdays with entries after 18:00
days_with_ot = set()
for line in lines:
    dt = parse_datetime(' '.join(line.split()[1:6]))
    if dt.weekday() < 5 and dt.time() >= datetime.time(18, 00):
        days_with_ot.add(dt.date())

# Function to check if the entry is from a valid day
def is_valid_entry(date_str):
    dt = parse_datetime(date_str)
    # Check if it's weekend or a weekday that qualifies as OT
    if dt.weekday() >= 5 or dt.date() in days_with_ot:
        return True
    return False

# Filter the lines
filtered_lines = [line for line in lines if is_valid_entry(' '.join(line.split()[1:6]))]

# Open new file
with open(input('Path to your output file (only txt for now): '), 'a') as f:
    # Print or write the filtered lines to another file
    for line in filtered_lines:
     print(line, file=f)


