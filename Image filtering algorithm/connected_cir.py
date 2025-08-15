import cv2
import os  # The os library provides common operations for directories and files
import shutil  # The shutil library supplements os, providing copy, move, delete, compress, and decompress operations
import numpy as np

if __name__ == '__main__':
    input_dir = "./images"  # Image folder path
    save_dir1 = "connected"  # Black connected path
    save_dir2 = "same"  # Isotropic
    save_dir3 = "different"  # Anisotropic
    same_thres = 0.9  # Threshold for isotropy; if the proportion of identical points exceeds 0.9, it's considered isotropic
    os.makedirs(save_dir1, exist_ok=True)  # Create folder using os module
    os.makedirs(save_dir2, exist_ok=True)
    os.makedirs(save_dir3, exist_ok=True)

    for file_name in os.listdir(input_dir):  # Iterate over files in the folder
        print("----------Processing %s----------" % file_name)
        file_path = os.path.join(input_dir, file_name)  # Join directory and file name to get full path
        # Read image
        img = cv2.imread(file_path)  # Read image
        # Median filtering to remove noise
        blur = cv2.medianBlur(img, 3)  # Circular shapes can be filtered
        # Convert to grayscale
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        # Threshold segmentation to obtain a binary image
        ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Invert the binary image
        binary = 255 - binary

        # Set pixels below the threshold to 0
        binary[binary < 200] = 0

        # Connected component analysis
        # num_labels: number of connected components
        # labels: label for each pixel (1, 2, 3, ...), same component has same label
        # stats: information for each component (x, y, width, height, area)
        # centroids: centroid of each component
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)  # 4 or 8 connectivity
        black_count = 0
        # Calculate mean grayscale of connected components to find number of black components
        for i in range(0, num_labels):
            mask = np.uint8(labels == i)
            mean_val = cv2.mean(binary, mask=mask)[0]
            if mean_val > 128:
                black_count += 1
        print("Number of black connected components: %d" % black_count)

        if black_count == 1:
            same_count = 0
            # Get image height and width
            height, width = binary.shape
            # Only traverse one quarter of the image to check isotropy
            for i in range(height // 2):
                for j in range(width // 2):
                    # Check if pixels are symmetric at 45 degrees
                    if binary[i, j] == binary[j, i]:
                        same_count += 1
            same_rate = same_count / (height * width // 4)
            print("Isotropy ratio:", same_rate)

            ###########################################################################################
            top = 0    # Whether the top row has black pixels
            down = 0   # Whether the bottom row has black pixels
            left = 0   # Whether the left column has black pixels
            right = 0  # Whether the right column has black pixels

            # Check top row
            for i in range(width):
                if blur[i, 0, 0] == 0:
                    top = 1
                    break
            # Check bottom row
            for i in range(width):
                if blur[i, -1, 0] == 0:
                    down = 1
                    break
            # Check left column
            for j in range(height):
                if blur[0, j, 0] == 0:
                    left = 1
                    break
            # Check right column
            for j in range(height):
                if blur[-1, j, 0] == 0:
                    right = 1
                    break

            # Only output if all four flags are 1
            if top == 1 and down == 1 and left == 1 and right == 1:
            ###########################################################################################
                # Before saving, set original image pixel values according to the binary result
                img[binary == 0] = 255  # Set binary black areas to white in the original image

                if same_rate > same_thres:
                    cv2.imwrite(os.path.join(save_dir2, file_name), img)
                else:
                    cv2.imwrite(os.path.join(save_dir3, file_name), img)
