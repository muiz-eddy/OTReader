import datetime
import csv

# Function to parse datetime from a formatted string
def parse_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")

# Dictionary to store the time bounds and commit IDs for each day
time_bounds = {}

# Read the git log output from a file
with open(input('Enter your file (in txt): '), 'r') as file:
    lines = file.readlines()

# Determine times by iterating over each log entry
for line in lines:
    parts = line.split()
    commit_id = parts[0]
    dt = parse_datetime(' '.join(parts[1:6]))

    date = dt.date()
    day = dt.strftime("%A")  
    if date not in time_bounds:
        time_bounds[date] = [dt, dt, day, {commit_id}]
    else:
        if dt < time_bounds[date][0]:
            time_bounds[date][0] = dt
        if dt > time_bounds[date][1]:
            time_bounds[date][1] = dt
        time_bounds[date][3].add(commit_id)

# Write the times, OT or not, to a CSV file
with open('times_summary_OT.csv', 'w', newline='') as csvfile:
    fieldnames = ['Date', 'Day', 'First Commit', 'Last Commit', 'Is OT','Is Weekend', 'OT Start Time', 'OT End Time', 'OT Duration (HH:MM)', 'Commit Ids']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for date, (first_commit, last_commit, day, commit_ids) in time_bounds.items():
        is_weekend = first_commit.weekday() >= 5
        weekday_ot_start_time = datetime.time(17, 15)
        ot_start_time = datetime.datetime.combine(date, weekday_ot_start_time) if not is_weekend else first_commit
        ot_end_time = last_commit if (not is_weekend and last_commit.time() >= weekday_ot_start_time) or is_weekend else None
        ot_duration = ot_end_time - ot_start_time if ot_end_time else datetime.timedelta(0)
        
        writer.writerow({
            'Date': date,
            'Day': day,
            'First Commit': first_commit.strftime('%H:%M:%S'),
            'Last Commit': last_commit.strftime('%H:%M:%S'),
            'Is OT': 'Yes' if (is_weekend or (not is_weekend and last_commit.time() >= weekday_ot_start_time)) else 'No',
            'Is Weekend': 'Yes' if (is_weekend) else 'No',
            'OT Start Time': ot_start_time.strftime('%H:%M:%S') if (is_weekend or (not is_weekend and last_commit.time() >= weekday_ot_start_time)) else '',
            'OT End Time': ot_end_time.strftime('%H:%M:%S') if ot_end_time else '',
            'OT Duration (HH:MM)': str(ot_duration).split('.')[0] if ot_duration else '',
            'Commit Ids': ', '.join(commit_ids)
        })

print("Summary of times, including OT and non-OT days, has been written to 'times_summary.csv'.")
