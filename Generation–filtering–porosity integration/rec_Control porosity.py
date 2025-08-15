import os, random
import numpy as np
from PIL import Image, ImageDraw

# ===== Utility Functions =====
def compute_porosity(img_arr):
    return np.count_nonzero(img_arr == 255) / img_arr.size

def forbid_point_to_point(binary):
    h, w = binary.shape
    for y in range(1, h - 1):
        row = binary[y]
        for x in range(1, w - 1):
            if row[x] == 255:
                if (binary[y - 1, x - 1] == 255 and binary[y, x - 1] == 0 and binary[y - 1, x] == 0): return False
                if (binary[y - 1, x + 1] == 255 and binary[y, x + 1] == 0 and binary[y - 1, x] == 0): return False
                if (binary[y + 1, x - 1] == 255 and binary[y, x - 1] == 0 and binary[y + 1, x] == 0): return False
                if (binary[y + 1, x + 1] == 255 and binary[y, x + 1] == 0 and binary[y + 1, x] == 0): return False
    return True

def black_single_component_and_touch_all_sides(binary):
    h, w = binary.shape
    # Check if black pixels touch all four edges
    if not ((binary[0, :] == 0).any() and (binary[-1, :] == 0).any() and
            (binary[:, 0] == 0).any() and (binary[:, -1] == 0).any()):
        return False
    visited = np.zeros_like(binary, dtype=bool)
    ys, xs = np.where(binary == 0)
    if len(xs) == 0: return False
    seed = (ys[0], xs[0])
    stack = [seed]
    visited[seed] = True
    cnt = 1
    total_black = (binary == 0).sum()
    nbrs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    while stack:
        y, x = stack.pop()
        for dy, dx in nbrs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and binary[ny, nx] == 0:
                visited[ny, nx] = True
                stack.append((ny, nx))
                cnt += 1
    return cnt == total_black

# ===== Draw Symmetric Squares =====
def draw_symmetric_square(draw, cx, cy, s, W, H, fill=255):
    qW, qH = W // 2, H // 2
    def _rect(xc, yc, ss):
        draw.rectangle([(xc - ss, yc - ss), (xc + ss, yc + ss)], fill=fill)
    if cx < cy:
        _rect(cx, cy, s); _rect(cy, cx, s)
    _rect(cx, 2 * qH - cy - 1, s); _rect(cy, 2 * qH - cx - 1, s)
    _rect(2 * qW - cx - 1, cy, s); _rect(2 * qW - cx - 1, cx, s)
    _rect(2 * qW - cx - 1, 2 * qH - cy - 1, s); _rect(2 * qW - cy - 1, 2 * qH - cx - 1, s)

def place_square_once(base_arr, cx, cy, s):
    H, W = base_arr.shape
    img = Image.fromarray(base_arr, mode='L')
    draw = ImageDraw.Draw(img)
    draw_symmetric_square(draw, cx, cy, s, W, H, fill=255)
    cand = np.array(img, dtype=np.uint8)
    if not forbid_point_to_point(cand): return None
    if not black_single_component_and_touch_all_sides(cand): return None
    return cand

# ===== Main Generation Function =====
def generate_square_images_constrained(
    output_folder,
    num_images=20,
    num_squares=10,
    s_min=8, s_max=20,          # Half side length range
    size=(256,256),
    phi_min=0.40, phi_max=0.60, # Porosity range
    max_attempts_per_image=2000,
    seed=None,
    verbose=True
):
    if seed is not None:
        random.seed(seed); np.random.seed(seed)
    os.makedirs(output_folder, exist_ok=True)
    W, H = size; qW, qH = W // 2, H // 2

    for idx in range(num_images):
        base = np.zeros((H, W), dtype=np.uint8)
        best = base.copy(); best_gap = 1e9
        placed = 0

        if verbose:
            print(f"\n[{idx+1}/{num_images}] Target φ∈[{phi_min:.2f},{phi_max:.2f}]")

        for attempts in range(1, max_attempts_per_image + 1):
            phi_now = compute_porosity(base)
            s_hi = s_max if phi_now < (phi_min + phi_max) / 2 else max(s_min, (s_min + s_max) // 2)
            s = random.randint(s_min, s_hi)
            cx = random.randint(0, qW - 1)
            cy = random.randint(cx + 1, qH - 1)

            cand = place_square_once(base, cx, cy, s)
            if cand is None:
                continue

            phi_tmp = compute_porosity(cand)
            gap = 0.0 if phi_min <= phi_tmp <= phi_max else min(abs(phi_tmp - phi_min), abs(phi_tmp - phi_max))
            if gap < best_gap:
                best_gap = gap; best = cand

            if phi_tmp <= phi_max:
                base = cand; placed += 1
                if verbose and placed % 2 == 0:
                    print(f"  ✔ Placed {placed}/{num_squares}, φ={phi_tmp:.3f}")
                if phi_tmp >= phi_min:
                    break
            if placed >= num_squares:
                continue

        final = base if (phi_min <= compute_porosity(base) <= phi_max) else best
        final_phi = compute_porosity(final)
        if verbose:
            ok = (phi_min <= final_phi <= phi_max)
            print(f"  Result φ={final_phi:.3f} {'✅Hit' if ok else '⚠Closest'}, placements={placed}")

        Image.fromarray(final, mode='L').convert("RGB").save(
            os.path.join(output_folder, f"{idx}.jpg")
        )

    print(f"\n✅ Images generated in folder: {output_folder}")

# ===== Example Call =====
if __name__ == "__main__":
    out_dir = "square_images_phi040_060"
    generate_square_images_constrained(
        output_folder=out_dir,
        num_images=5,
        num_squares=10,
        s_min=10, s_max=18,       # Half side length range
        size=(256,256),
        phi_min=0.40, phi_max=0.60,
        max_attempts_per_image=2000,
        seed=0
    )
