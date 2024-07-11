import datetime
import csv

# Function to parse datetime from a formatted string
def parse_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")

# Dictionary to store the earliest and latest OT times for each day, including weekends
ot_time_bounds = {}

# Read the git log output from a file
with open(input('Enter your file (in txt): '), 'r') as file:
    lines = file.readlines()

# Determine OT times by iterating over each log entry
for line in lines:
    parts = line.split()
    commit_id = parts[0]
    dt = parse_datetime(' '.join(parts[1:6]))

    # OT starts at 17:15 on weekdays
    weekday_ot_start_time = datetime.time(17, 15)
    is_weekend = dt.weekday() >= 5
    is_after_ot_start = dt.time() >= weekday_ot_start_time
    if (dt.weekday() < 5 and is_after_ot_start) or is_weekend:
        date = dt.date()
        day = dt.strftime("%A")  
        if date not in ot_time_bounds:
            start_time = datetime.datetime.combine(date, weekday_ot_start_time) if not is_weekend else dt
            ot_time_bounds[date] = [start_time, dt, day, {commit_id}]
        else:
            if dt < ot_time_bounds[date][0]:
                ot_time_bounds[date][0] = dt
            if dt > ot_time_bounds[date][1]:
                ot_time_bounds[date][1] = dt
            ot_time_bounds[date][3].add(commit_id)

# Write the OT start, end times, and duration to a CSV file
with open('ot_times.csv', 'w', newline='') as csvfile:
    fieldnames = ['Date', 'Day', 'Start Time', 'End Time', 'Duration (HH:MM)', 'Commit Id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for date, (start_time, end_time, day, commit_ids) in ot_time_bounds.items():
        # Calculate duration based on the corrected start time
        duration = end_time - start_time
        writer.writerow({
            'Date': date,
            'Day': day,
            'Start Time': start_time.strftime('%H:%M:%S'),
            'End Time': end_time.strftime('%H:%M:%S'),
            'Duration (HH:MM)': str(duration).split('.')[0],
            'Commit Id': ', '.join(commit_ids)
        })

print("OT times with days of the week, including duration, have been written to 'ot_times.csv'.")
