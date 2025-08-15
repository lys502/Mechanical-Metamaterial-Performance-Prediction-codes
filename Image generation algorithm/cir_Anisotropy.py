from PIL import Image, ImageDraw
import os
import random

def generate_images(output_folder, num_images, num_circles):
    # Create the output folder
    os.makedirs(output_folder, exist_ok=True)

    # Set image size
    image_size = (256, 256)

    for i in range(num_images):
        # Create a completely black image
        img = Image.new("RGB", image_size, "black")
        draw = ImageDraw.Draw(img)

        # Calculate the size of each quarter
        quarter_width = image_size[0] // 2
        quarter_height = image_size[1] // 2

        for _ in range(num_circles):
            # Randomly generate circle parameters
            radius = random.randint(10, 31)  # Random circle radius range, can also be fixed
            center_x = random.randint(0, quarter_width)
            center_y = random.randint(0, quarter_height)

            # Draw a white filled circle in the top-left quadrant
            draw.ellipse([(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], fill="white")

            # Mirror to generate bottom-left white filled circle
            draw.ellipse([(center_x - radius, 2 * quarter_height - center_y - radius - 0.5),
                          (center_x + radius, 2 * quarter_height - center_y + radius - 0.5)], fill="white")

            # Mirror to generate top-right white filled circle
            draw.ellipse([(2 * quarter_width - center_x - radius - 0.5, center_y - radius),
                          (2 * quarter_width - center_x + radius - 0.5, center_y + radius)], fill="white")

            # Mirror to generate bottom-right white filled circle
            draw.ellipse([(2 * quarter_width - center_x - radius - 0.5, 2 * quarter_height - center_y - radius - 0.5),
                          (2 * quarter_width - center_x + radius - 0.5, 2 * quarter_height - center_y + radius - 0.5)], fill="white")

        # Save the image
        img.save(os.path.join(output_folder, f"{i}.jpg"))

# Generate and save images
output_folder = "images"
num_images = 40
num_circles = 16
generate_images(output_folder, num_images, num_circles)
