import cv2
import os
import shutil
import pandas as pd
from tqdm import tqdm


def has_point_to_point_connection(image_path):
    # Read the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return False

    # Binarize the image (invert colors so black becomes white for detection)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

    # Get image dimensions
    height, width = binary.shape

    # Check each black pixel for point-to-point connections
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if binary[y, x] == 255:  # Current pixel is black
                # Check diagonal point-to-point connections
                if (binary[y - 1, x - 1] == 255 and binary[y, x - 1] == 0 and binary[y - 1, x] == 0) or \
                   (binary[y - 1, x + 1] == 255 and binary[y, x + 1] == 0 and binary[y - 1, x] == 0) or \
                   (binary[y + 1, x - 1] == 255 and binary[y, x - 1] == 0 and binary[y + 1, x] == 0) or \
                   (binary[y + 1, x + 1] == 255 and binary[y, x + 1] == 0 and binary[y + 1, x] == 0):
                    return True

    return False


def filter_and_move_images(src_folder, dest_folder, excel_path):
    unqualified_images = []

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    file_list = [f for f in os.listdir(src_folder) if f.endswith(".png") or f.endswith(".jpg")]

    for filename in tqdm(file_list, desc="Processing images"):
        image_path = os.path.join(src_folder, filename)
        if has_point_to_point_connection(image_path):
            unqualified_images.append(filename)
            shutil.move(image_path, os.path.join(dest_folder, filename))

    # Save the names of unqualified images to an Excel file
    df = pd.DataFrame(unqualified_images, columns=['Unqualified Images'])
    df.to_excel(excel_path, index=False)


# Example: Filter and move unqualified images from a folder, save their names to Excel
src_folder = "images_cir"  # Source folder path
dest_folder = "unqualified_images"  # Destination folder for unqualified images
excel_path = "unqualified_images.xlsx"  # Output Excel file path

filter_and_move_images(src_folder, dest_folder, excel_path)
print("Unqualified images have been moved to the new folder and recorded in the Excel file.")
