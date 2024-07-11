import datetime
import csv

# Function to parse datetime from a formatted string
def parse_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")

# Dictionary to store the time bounds, commit IDs, and commit times for each day
time_bounds = {}

# Read the git log output from a file
filename = input('Enter your file (in txt): ')
with open(filename, 'r') as file:
    lines = file.readlines()

# Determine times by iterating over each log entry
for line in lines:
    parts = line.split()
    commit_id = parts[0]
    dt = parse_datetime(' '.join(parts[1:6]))

    date = dt.date()
    day = dt.strftime("%A")
    if date not in time_bounds:
        time_bounds[date] = [dt, dt, day, set([commit_id]), [dt]]
    else:
        if dt < time_bounds[date][0]:
            time_bounds[date][0] = dt
        if dt > time_bounds[date][1]:
            time_bounds[date][1] = dt
        time_bounds[date][3].add(commit_id)
        time_bounds[date][4].append(dt)

output_filename = input('Name of the output file (in csv): ')

include_non_ot = input("Do you want to include non-OT days in the output? (yes/no): ").lower().strip()

total_seconds = 0

# Write the times, OT or not, to a CSV file
with open(output_filename, 'w', newline='') as csvfile:
    fieldnames = ['Date', 'Day', 'First Commit', 'Last Commit', 'Is Weekend', 'Is OT', 'OT Start Time', 'OT End Time', 'OT Duration (HH:MM)', 'Commit Ids']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for date, (first_commit, last_commit, day, commit_ids, commit_times) in time_bounds.items():
        is_weekend = first_commit.weekday() >= 5
        weekday_ot_start_time = datetime.time(17, 15)
        if not is_weekend:
            commit_times_after_1715 = [dt for dt in commit_times if dt.time() >= weekday_ot_start_time]
            if commit_times_after_1715:
                ot_start_time = min(commit_times_after_1715)
                ot_end_time = last_commit
                if len(commit_times_after_1715) == 1:  # If there's only one commit after 17:15
                    ot_duration = datetime.timedelta(hours=1)  # Set duration to one hour
                else:
                    ot_duration = ot_end_time - ot_start_time
            else:
                ot_start_time = None
                ot_end_time = None
                ot_duration = datetime.timedelta(0)
        else:
            ot_start_time = first_commit
            ot_end_time = last_commit
            ot_duration = ot_end_time - ot_start_time

        total_seconds += ot_duration.total_seconds()

        # Write row based on user choice
        if ot_start_time or include_non_ot == "yes":
            writer.writerow({
                'Date': date,
                'Day': day,
                'First Commit': first_commit.strftime('%H:%M:%S'),
                'Last Commit': last_commit.strftime('%H:%M:%S'),
                'Is Weekend': 'Yes' if is_weekend else 'No',
                'Is OT': 'Yes' if ot_start_time else 'No',
                'OT Start Time': ot_start_time.strftime('%H:%M:%S') if ot_start_time else '',
                'OT End Time': ot_end_time.strftime('%H:%M:%S') if ot_end_time else '',
                'OT Duration (HH:MM)': str(ot_duration).split('.')[0] if ot_duration else '',
                'Commit Ids': ', '.join(commit_ids)
            })

    # Convert total_seconds to hours and minutes
    total_hours = int(total_seconds // 3600)
    total_minutes = int((total_seconds % 3600) / 60)
    total_duration_formatted = f"{total_hours:02}:{total_minutes:02}"

    # Write the total duration row
    writer.writerow({
        'Date': 'Total Duration',
        'OT Duration (HH:MM)': total_duration_formatted
    })

print(f"Summary of times, including OT and non-OT days with weekend indication, has been written to '{output_filename}'.")