from PIL import Image, ImageDraw
import os
import random

def generate_images(output_folder, num_images, num_squares):
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

        for _ in range(num_squares):
            # Randomly generate square parameters
            side_length = random.randint(10, 11)  # Range for the square's side length
            # Ensure coordinates are within bounds
            x = random.randint(side_length, quarter_width)
            y = random.randint(side_length, quarter_height)

            # Draw a white filled square in the top-left quadrant
            draw.rectangle([(x - side_length, y - side_length), (x + side_length, y + side_length)], fill="white")

            # Mirror to generate bottom-left white filled square
            draw.rectangle([(x - side_length,  2 * quarter_height - y - side_length - 0.5),
                            (x + side_length, 2 * quarter_height - y + side_length - 0.5)], fill="white")

            # Mirror to generate top-right white filled square
            draw.rectangle([(2 * quarter_width - x - side_length - 0.5, y - side_length),
                            (2 * quarter_width - x + side_length - 0.5, y + side_length)], fill="white")

            # Mirror to generate bottom-right white filled square
            draw.rectangle([(2 * quarter_width - x - side_length - 0.5, 2 * quarter_height - y - side_length - 0.5),
                            (2 * quarter_width - x + side_length - 0.5, 2 * quarter_height - y + side_length - 0.5)], fill="white")

        # Save the image
        img.save(os.path.join(output_folder, f"{i}.jpg"))

# Generate and save images
output_folder = "images"
num_images = 40
num_squares = 20
generate_images(output_folder, num_images, num_squares)
