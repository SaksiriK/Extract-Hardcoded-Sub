import json
import cv2
from tkinter import filedialog
import tkinter as tk
# starting suggestions
#Image dimensions: 3840 x 250 pixels
#Start X: 1300
#End X: 2600
#Upper Y: 50
#Lower Y: 200
def select_image_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image files", "*.jpg;*.png")])
    root.destroy()
    return file_path

def select_json_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON files", "*.json")])
    root.destroy()
    return file_path

def print_image_dimensions(image_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to read image at {image_path}.")
        return

    # Get image dimensions
    height, width, _ = image.shape
    print(f"Image dimensions: {width} x {height} pixels")

def set_subtitle_area():
    print("Select a JSON file...")
    # Select the JSON file
    json_file_path = select_json_file()
    if not json_file_path:
        print("No JSON file selected. Exiting.")
        return

    print("Selected JSON file:", json_file_path)

    # Read the JSON file to get cropping parameters
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            cropping_params = json.load(f)
    except FileNotFoundError:
        print("JSON file not found. Using image dimensions as initial cropping parameters.")
        image_path = select_image_file()
        if not image_path:
            print("No image file selected. Exiting.")
            return
        print_image_dimensions(image_path)  # Print dimensions after selecting the image
        image = cv2.imread(image_path)
        image_height, image_width, _ = image.shape
        cropping_params = {
            "start_x": 0,
            "end_x": image_width,
            "upper_y": 0,
            "lower_y": image_height
        }

    # Loop to allow user to adjust crop area
    while True:
        # Select the image file
        print("Selected JSON file:", json_file_path)
        image_path = select_image_file()
        if not image_path:
            print("No image file selected. Exiting.")
            return

        print("Selected image file:", image_path)
        print_image_dimensions(image_path)  # Print dimensions after selecting the image

        # Read the image
        image = cv2.imread(image_path)
        image_height, image_width, _ = image.shape

        # Extract cropping parameters from JSON
        start_x = cropping_params.get("start_x", 0)
        end_x = cropping_params.get("end_x", image_width)
        upper_y = cropping_params.get("upper_y", 0)
        lower_y = cropping_params.get("lower_y", image_height)

        print("Old Cropping parameters:")
        print("Start X:", start_x)
        print("End X:", end_x)
        print("Upper Y:", upper_y)
        print("Lower Y:", lower_y)

        # Define the cropping rectangle
        start_point = (start_x, upper_y)
        end_point = (end_x, lower_y)

        # Draw a rectangle to show the cropped area
        color = (0, 255, 0)  # Green color for the rectangle
        thickness = 2        # Thickness of the rectangle border
        image_with_rectangle = cv2.rectangle(image.copy(), start_point, end_point, color, thickness)

        # Display the image with the cropped area highlighted
        print("Showing image with cropped area highlighted...")
        cv2.imshow('Image with Cropped Area Highlighted', image_with_rectangle)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Perform the crop
        cropped_image = image[upper_y:lower_y, start_x:end_x]

        # Display the cropped image
        print("Showing cropped image...")
        cv2.imshow('Cropped Image', cropped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Ask user if crop is correct
        user_input = input("Is the crop area correct? (Y/N): ").strip().lower()
        if user_input == 'y':
            # Write the cropping parameters back to the JSON file
            print("Writing cropping parameters to JSON file...")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(cropping_params, f, indent=4)
            print("Cropping parameters saved to:", json_file_path)
            break
        elif user_input == 'n':
            # Ask user to adjust crop limits
            print("Adjusting crop limits...")
            start_x = int(input(f"Enter new value for Start X (old value: {start_x}): ").strip() or start_x)
            end_x = int(input(f"Enter new value for End X (old value: {end_x}): ").strip() or end_x)
            upper_y = int(input(f"Enter new value for Upper Y (old value: {upper_y}): ").strip() or upper_y)
            lower_y = int(input(f"Enter new value for Lower Y (old value: {lower_y}): ").strip() or lower_y)
            # Update cropping parameters
            cropping_params['start_x'] = start_x
            cropping_params['end_x'] = end_x
            cropping_params['upper_y'] = upper_y
            cropping_params['lower_y'] = lower_y

# Call the function to set the subtitle area
set_subtitle_area()