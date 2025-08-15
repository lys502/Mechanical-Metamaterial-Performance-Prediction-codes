import os
import cv2
import random
import numpy as np

def get_neighbor(img, width, height):
    neighbors = []
    for i in range(width // 2):
        for j in range(height // 2):
            if img[i, j, 0] == 255 and img[i, j, 1] == 255 and img[i, j, 2] == 255:
                continue
            else:
                if i - 1 >= 0 and j - 1 >= 0:
                    if img[i - 1, j - 1, 0] == 255:
                        neighbors.append([i, j])
                        continue
                if j - 1 >= 0:
                    if img[i, j - 1, 0] == 255:
                        neighbors.append([i, j])
                        continue
                if i + 2 <= width // 2 and j - 1 >= 0:
                    if img[i + 1, j - 1, 0] == 255:
                        neighbors.append([i, j])
                        continue
                if i - 1 >= 0:
                    if img[i - 1, j, 0] == 255:
                        neighbors.append([i, j])
                        continue
                if i + 2 <= width // 2:
                    if img[i + 1, j, 0] == 255:
                        neighbors.append([i, j])
                        continue
                if i - 1 >= 0 and j + 2 <= height // 2:
                    if img[i - 1, j + 1, 0] == 255:
                        neighbors.append([i, j])
                        continue
                if j + 2 <= height // 2:
                    if img[i, j + 1, 0] == 255:
                        neighbors.append([i, j])
                        continue
                if i + 2 <= width // 2 and j + 2 <= height // 2:
                    if img[i + 1, j + 1, 0] == 255:
                        neighbors.append([i, j])
                        continue
    return neighbors

def compute_porosity(img, width, height):
    count = 0
    for i in range(width // 2):
        for j in range(height // 2):
            if img[i, j, 0] == 255 and img[i, j, 1] == 255 and img[i, j, 2] == 255:
                count += 1
    return count / (width * height) * 4

if __name__ == '__main__':
    porosity = 0.4
    num_point = 40
    width = 256
    height = 256
    num_image = 500
    growthrate = 0.5
    save_dir = "./images"
    os.makedirs(save_dir, exist_ok=True)

    for img_name in range(num_image):
        print("Generating image %d" % img_name)
        img = np.zeros((width, height, 3), np.uint8)

        print("First growth")
        for i in range(num_point // 4):
            x1 = random.randint(0, width // 2 - 1)
            y1 = random.randint(0, height // 2 - 1)
            # Generate points in the lower-left part of the diagonal,
            # then mirror them across the diagonal to the upper-right part
            img[x1, y1] = (255, 255, 255)
            img[x1, height - 1 - y1] = (255, 255, 255)
            img[width - 1 - x1, y1] = (255, 255, 255)
            img[width - 1 - x1, height - 1 - y1] = (255, 255, 255)

        curr_porosity = compute_porosity(img, width, height)
        print("Current porosity:", curr_porosity)

        if curr_porosity >= porosity:
            cv2.imwrite(os.path.join(save_dir, str(img_name) + ".jpg"), img)

        else:
            flag = 2
            while True:
                print("Growth step %d" % flag)
                neighbors = get_neighbor(img, width, height)
                growthnum = int(len(neighbors) * growthrate)
                choose_neighbors = random.sample(neighbors, growthnum)
                for pos in choose_neighbors:
                    x1, y1 = pos[0], pos[1]
                    img[x1, y1] = (255, 255, 255)
                    img[x1, height - 1 - y1] = (255, 255, 255)
                    img[width - 1 - x1, y1] = (255, 255, 255)
                    img[width - 1 - x1, height - 1 - y1] = (255, 255, 255)

                    # Mirror to the upper-right part along the diagonal
                    # (swap x and y from the above four lines)
                    img[width - 1 - y1, x1] = (255, 255, 255)
                    img[width - 1 - y1, height - 1 - x1] = (255, 255, 255)
                    img[y1, x1] = (255, 255, 255)
                    img[y1, height - 1 - x1] = (255, 255, 255)

                curr_porosity = compute_porosity(img, width, height)
                print("Current porosity:", curr_porosity)
                flag += 1
                if curr_porosity >= porosity:
                    break
            cv2.imwrite(os.path.join(save_dir, str(img_name) + ".jpg"), img)
