import datetime
import csv

def parse_datetime(date_str):
    """Parse a datetime string into a datetime object."""
    return datetime.datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")

def read_git_log(filename):
    """Reads the git log from a file and parses the commit times."""
    time_bounds = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
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
    return time_bounds

def write_ot_times(output_filename, time_bounds, include_non_ot):
    """Writes OT times to a CSV file based on user preferences."""
    total_seconds = 0
    with open(output_filename, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Day', 'First Commit', 'Last Commit', 'Is Weekend', 'Is OT', 'OT Start Time', 'OT End Time', 'OT Duration (HH:MM)', 'Commit Ids']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for date, (first_commit, last_commit, day, commit_ids, commit_times) in time_bounds.items():
            is_weekend = first_commit.weekday() >= 5
            weekday_ot_start_time = datetime.time(17, 15)
            ot_start_time, ot_end_time, ot_duration = handle_ot_calculation(commit_times, last_commit, is_weekend, weekday_ot_start_time)
            total_seconds += ot_duration.total_seconds()
            if ot_start_time or include_non_ot == "yes":
                writer.writerow(create_row(date, day, first_commit, last_commit, is_weekend, ot_start_time, ot_end_time, ot_duration, commit_ids))
        write_total_duration(writer, total_seconds)

def handle_ot_calculation(commit_times, last_commit, is_weekend, ot_start_time_threshold):
    """Handles the calculation of OT start, end, and duration."""
    if not is_weekend:
        commit_times_after_1715 = [dt for dt in commit_times if dt.time() >= ot_start_time_threshold]
        if commit_times_after_1715:
            ot_start_time = min(commit_times_after_1715)
            ot_end_time = last_commit
            ot_duration = datetime.timedelta(hours=1) if len(commit_times_after_1715) == 1 else ot_end_time - ot_start_time
        else:
            ot_start_time = ot_end_time = ot_duration = None
    else:
        ot_start_time = commit_times[0]
        ot_end_time = last_commit
        ot_duration = ot_end_time - ot_start_time
    return ot_start_time, ot_end_time, ot_duration if ot_duration else datetime.timedelta(0)

def create_row(date, day, first_commit, last_commit, is_weekend, ot_start_time, ot_end_time, ot_duration, commit_ids):
    """Creates a dictionary for a row to be written to the CSV."""
    return {
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
    }

def write_total_duration(writer, total_seconds):
    """Writes the total duration to the CSV file."""
    total_hours = int(total_seconds // 3600)
    total_minutes = int((total_seconds % 3600) / 60)
    writer.writerow({'Date': 'Total Duration', 'OT Duration (HH:MM)': f"{total_hours:02}:{total_minutes:02}"})

def main():
    filename = input('Enter your file (in txt): ')
    time_bounds = read_git_log(filename)
    output_filename = input('Name of the output file (in csv): ')
    include_non_ot = input("Do you want to include non-OT days in the output? (yes/no): ").lower().strip()
    write_ot_times(output_filename, time_bounds, include_non_ot)
    print(f"Summary of times, including OT and non-OT days with weekend indication, has been written to '{output_filename}'.")

if __name__ == "__main__":
    main()
