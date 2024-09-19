import pandas as pd
from datetime import timedelta

# Specify the input and output file paths
input_file_path = 'D:\\Gensub\\XtractHDsub\\ocr_results.xlsx'
output_excel_path = 'D:\\Gensub\\XtractHDsub\\combinesubs.xlsx'
output_srt_path = 'D:\\Gensub\\XtractHDsub\\combinesubs.srt'

# Read the input Excel file
df = pd.read_excel(input_file_path, header=None, names=['Filename', 'Start Time', 'Text'])

# Remove the last row from the DataFrame to exclude any end-of-data markers
df = df.iloc[:-1]

# Convert 'Start Time' to numeric type, coercing errors to NaN
df['Start Time'] = pd.to_numeric(df['Start Time'], errors='coerce')

# Remove any rows with NaN in 'Start Time' or 'Text'
df.dropna(subset=['Start Time', 'Text'], inplace=True)

# Initialize the list to store the processed rows
processed_rows = []
srt_lines = []

# Initialize counters for summary
total_lines = len(df)
combined_lines = 0


# Function to convert time in seconds to SRT time format
def format_srt_time(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.microseconds / 1000))
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


# Check again that the DataFrame is not empty after trimming
if df.empty:
    raise ValueError("The DataFrame is empty after trimming the end-of-data line. Please check the input data.")

# Set the first row as the anchor line
anchor_filename = df.iloc[0]['Filename']
anchor_start_time = df.iloc[0]['Start Time']
anchor_text = df.iloc[0]['Text']
anchor_end_time = anchor_start_time + 1  # Initialize ending time as starting time + 1 second

# Iterate over the DataFrame starting from the second row
for index in range(1, len(df)):
    current_filename = df.iloc[index]['Filename']
    current_start_time = df.iloc[index]['Start Time']
    current_text = df.iloc[index]['Text']

    # Compare text of anchor line and current line
    if current_text == anchor_text:
        # If texts match, extend the ending time of the anchor line
        anchor_end_time += 1
        combined_lines += 1
    else:
        # If texts do not match, determine the duration and adjust if necessary
        duration = anchor_end_time - anchor_start_time

        # Check if duration is less than or equal to 1 second
        if duration <= 1:
            # Try to increase the duration to 2 seconds
            proposed_end_time = anchor_start_time + 2
            if proposed_end_time <= current_start_time:
                anchor_end_time = proposed_end_time
            else:
                print(f"Overlap detected: Keeping duration at 1 second for subtitle starting at {anchor_start_time}")

                # Write the anchor line to the processed rows if the duration is appropriate
        duration = anchor_end_time - anchor_start_time
        processed_rows.append([anchor_filename, anchor_start_time, anchor_end_time, duration, anchor_text])

        # Write the line to the SRT file format
        srt_index = len(srt_lines) + 1
        srt_start_time = format_srt_time(anchor_start_time)
        srt_end_time = format_srt_time(anchor_end_time)
        srt_lines.append(f"{srt_index}\n{srt_start_time} --> {srt_end_time}\n{anchor_text}\n")

        # Move the current line to the anchor line
        anchor_filename = current_filename
        anchor_start_time = current_start_time
        anchor_text = current_text
        anchor_end_time = anchor_start_time + 1

    # Add the last anchor line to the processed rows and SRT lines
duration = anchor_end_time - anchor_start_time
if duration <= 1:
    anchor_end_time = anchor_start_time + 2
duration = anchor_end_time - anchor_start_time
processed_rows.append([anchor_filename, anchor_start_time, anchor_end_time, duration, anchor_text])
srt_index = len(srt_lines) + 1
srt_start_time = format_srt_time(anchor_start_time)
srt_end_time = format_srt_time(anchor_end_time)
srt_lines.append(f"{srt_index}\n{srt_start_time} --> {srt_end_time}\n{anchor_text}\n")

# Create a DataFrame from the processed rows
processed_df = pd.DataFrame(processed_rows, columns=['Filename', 'Start Time', 'End Time', 'Duration', 'Text'])

# Write the processed DataFrame to a new Excel file
processed_df.to_excel(output_excel_path, index=False)
print(f"Processed Excel file has been saved to {output_excel_path}")

# Write the SRT lines to a new SRT file
with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
    srt_file.write("\n".join(srt_lines))

print(f"SRT file has been saved to {output_srt_path}")

# Print summary
print("\nSummary:")
print(f"Total lines processed: {total_lines}")
print(f"Total lines combined: {combined_lines}")
print(f"Total unique subtitles: {len(processed_rows)}")