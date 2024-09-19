import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


def select_video_file():
    # Open a file dialog to select a video file
    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mp4;*.mov;*.avi;*.mkv;*.flv;*.wmv")]
    )
    if file_path:
        video_path.set(file_path)
        get_video_info(file_path)


def get_video_info(video_file):
    # Use ffprobe to get video dimensions
    try:
        output = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of",
             "default=noprint_wrappers=1:nokey=1", video_file]
        ).decode('utf-8').strip().splitlines()

        if len(output) == 2:
            width.set(output[0])
            height.set(output[1])
            messagebox.showinfo("Video Info", f"Width: {output[0]}, Height: {output[1]}")
        else:
            messagebox.showerror("Error", "Could not retrieve video dimensions.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error retrieving video info: {e}")


def build_ffmpeg_command():
    video_file = video_path.get()
    video_dir = os.path.dirname(video_file)
    frame_dir = os.path.join(video_dir, "frames")
    frame_output = os.path.join(frame_dir, "frame_%04d.png")
    metadata_file = os.path.join(video_dir, "metadata.txt")

    # Create frames directory if it doesn't exist
    os.makedirs(frame_dir, exist_ok=True)

    # Get video dimensions
    video_width = int(width.get())
    video_height = int(height.get())

    # Define crop parameters (assuming we want the lower part of the video)
    crop_height = video_height // 4  # Crop the lower quarter of the video
    crop_y = video_height - crop_height  # Y coordinate for cropping

    # Build the FFmpeg command to extract frames from the lower part of the video
    ffmpeg_command = f'ffmpeg -i "{video_file}" -vf "crop={video_width}:{crop_height}:0:{crop_y},fps=1" -q:v 2 "{frame_output}"'

    # Run the command in CMD
    try:
        subprocess.run(ffmpeg_command, shell=True)
        messagebox.showinfo("Success", "Frames extracted successfully!")

        # Generate metadata file
        generate_metadata_file(frame_dir, metadata_file)

        root.destroy()  # Close the GUI after extraction
    except Exception as e:
        messagebox.showerror("Error", f"Error running FFmpeg command: {e}")


def generate_metadata_file(frame_dir, metadata_file):
    try:
        # Get the list of extracted frames
        frame_files = sorted(os.listdir(frame_dir))

        with open(metadata_file, 'w') as f:
            for i, frame_file in enumerate(frame_files):
                # Calculate elapsed time in seconds
                elapsed_time = i  # Assuming 1 frame per second
                f.write(f"{frame_file}, {elapsed_time:.2f}\n")

        messagebox.showinfo("Success", f"Metadata file created at: {metadata_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Error writing metadata file: {e}")

    # Create the main window


root = tk.Tk()
root.title("Video Frame Extractor")

# Variables to hold video path and dimensions
video_path = tk.StringVar()
width = tk.StringVar()
height = tk.StringVar()

# Create GUI elements
tk.Label(root, text="Selected Video File:").pack(pady=5)
tk.Entry(root, textvariable=video_path, width=50).pack(pady=5)
tk.Button(root, text="Browse", command=select_video_file).pack(pady=5)

tk.Button(root, text="Extract Frames and Build Metadata", command=build_ffmpeg_command).pack(pady=20)

# Start the GUI event loop
root.mainloop()