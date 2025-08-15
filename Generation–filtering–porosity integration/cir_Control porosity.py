import os, random
import numpy as np
from PIL import Image, ImageDraw

# ---------- Utility functions ----------
def compute_porosity(img_arr):
    # Proportion of white pixels
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

def draw_symmetric_disk(draw, cx, cy, r, W, H, fill=255):
    qW, qH = W // 2, H // 2
    def _ellipse(cxx, cyy, rr):
        draw.ellipse([(cxx - rr, cyy - rr), (cxx + rr, cyy + rr)], fill=fill)
    if cx < cy:
        _ellipse(cx, cy, r); _ellipse(cy, cx, r)
    _ellipse(cx, 2 * qH - cy - 1, r); _ellipse(cy, 2 * qH - cx - 1, r)
    _ellipse(2 * qW - cx - 1, cy, r); _ellipse(2 * qW - cx - 1, cx, r)
    _ellipse(2 * qW - cx - 1, 2 * qH - cy - 1, r); _ellipse(2 * qW - cy - 1, 2 * qH - cx - 1, r)

def place_once(base_arr, cx, cy, r):
    H, W = base_arr.shape
    img = Image.fromarray(base_arr, mode='L')  # No copy, will not write back if failed
    draw = ImageDraw.Draw(img)
    draw_symmetric_disk(draw, cx, cy, r, W, H, fill=255)
    cand = np.array(img, dtype=np.uint8)
    if not forbid_point_to_point(cand): return None
    if not black_single_component_and_touch_all_sides(cand): return None
    return cand

# ---------- Main function ----------
def generate_images_constrained(
    output_folder,
    num_images=20,
    num_disks=10,
    r_min=8, r_max=20,
    size=(256, 256),
    phi_min=0.40, phi_max=0.60,
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

        if verbose: print(f"\n[{idx+1}/{num_images}] Target φ∈[{phi_min:.2f},{phi_max:.2f}]")

        for attempts in range(1, max_attempts_per_image + 1):
            # Dynamically shrink radius upper limit: when close to upper bound, prefer smaller radius
            phi_now = compute_porosity(base)
            r_hi = r_max if phi_now < (phi_min + phi_max) / 2 else max(r_min, (r_min + r_max) // 2)
            r = random.randint(r_min, r_hi)
            cx = random.randint(0, qW - 1)
            cy = random.randint(cx + 1, qH - 1)

            cand = place_once(base, cx, cy, r)
            if cand is None:
                if verbose and attempts % 500 == 0:
                    print(f"  ...Attempt {attempts}, still searching for feasible placement")
                continue

            phi_tmp = compute_porosity(cand)
            # Record candidate "closest to interval"
            gap = 0.0 if phi_min <= phi_tmp <= phi_max else min(abs(phi_tmp - phi_min), abs(phi_tmp - phi_max))
            if gap < best_gap:
                best_gap = gap; best = cand

            if phi_tmp <= phi_max:
                base = cand; placed += 1
                if verbose and placed % 2 == 0:
                    print(f"  ✔ Placed {placed}/{num_disks}, φ={phi_tmp:.3f}")
                # ✅ Stop once entering interval
                if phi_tmp >= phi_min:
                    break
                # If still below lower bound but near upper bound, will automatically shrink radius

            # Optional: Limit max placement attempts (like "max num_disks successful placements")
            if placed >= num_disks:
                # If reached limit but not in interval, continue fine-tuning (using random small radius)
                continue

        final = base if (phi_min <= compute_porosity(base) <= phi_max) else best
        final_phi = compute_porosity(final)
        if verbose:
            ok = (phi_min <= final_phi <= phi_max)
            print(f"  Result φ={final_phi:.3f} {'✅Hit' if ok else '⚠Closest'}, placements={placed}")

        Image.fromarray(final, mode='L').convert("RGB").save(
            os.path.join(output_folder, f"{idx}.jpg")
        )

    print(f"\n✅ Generated images saved to folder: {output_folder}")

if __name__ == "__main__":
    print("cwd =", os.getcwd())

    # Low porosity ~0.25-0.40
    # generate_images_constrained("phi_025_040", num_images=5, num_disks=6, r_min=10, r_max=18, phi_min=0.25, phi_max=0.40, seed=0)

    # Medium porosity ~0.55-0.70
    # generate_images_constrained("phi_055_070", num_images=5, num_disks=12, r_min=14, r_max=20, phi_min=0.55, phi_max=0.70, seed=0)

    # Higher porosity ~0.70-0.80 (your case)
    generate_images_constrained("phi_070_080", num_images=5, num_disks=16, r_min=12, r_max=18,
                                phi_min=0.40, phi_max=0.50, max_attempts_per_image=4000, seed=0)
