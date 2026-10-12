import os
import glob
import cv2
from datetime import datetime

INPUT_DIR = "./riverside_camera"
OUTPUT_DIR = "./riverside_loop"
TARGET_IMAGES = 550
MASK_RATIO = 0.14

START_FRAME = "img_20260319_131704_543110.png"
END_FRAME = "img_20260319_131814_501219.png"

def parse_timestamp(filename):
    """Extracts the UNIX timestamp from the filename."""
    base_name = os.path.basename(filename)
    time_str = base_name.replace("img_", "").replace(".png", "")
    dt = datetime.strptime(time_str, "%Y%m%d_%H%M%S_%f")
    return dt.timestamp()

def main():
    rgb_dir = os.path.join(OUTPUT_DIR, "rgb")
    os.makedirs(rgb_dir, exist_ok=True)
    
    search_pattern = os.path.join(INPUT_DIR, "img_*.png")
    all_images = sorted(glob.glob(search_pattern))
    
    if not all_images:
        print("Error: No images found matching the pattern.")
        return

    basenames = [os.path.basename(p) for p in all_images]
    
    try:
        # SKIP the START_FRAME
        start_idx = basenames.index(START_FRAME) + 1
        end_idx = basenames.index(END_FRAME) + 1 
    except ValueError as e:
        print(f"Error finding frames: {e}. Check filenames.")
        return
        
    sequence_images = all_images[start_idx:end_idx]
    num_frames = len(sequence_images)
    print(f"Frames in window: {num_frames}")

    if num_frames <= TARGET_IMAGES:
        selected_images = sequence_images
        print(f"Warning: Only {num_frames} available. Extracting all.")
    else:
        
        indices = [int(i * (num_frames - 1) / (TARGET_IMAGES - 1)) for i in range(TARGET_IMAGES)]
        selected_images = [sequence_images[i] for i in indices]

    print(f"Extracting exactly {len(selected_images)} masked images...")

    rgb_txt_path = os.path.join(OUTPUT_DIR, "rgb.txt")
    
    with open(rgb_txt_path, "w") as f:
        f.write("# color images\n# file: 'rgb.txt'\n# timestamp filename\n")
        
        for i, original_path in enumerate(selected_images):
            new_filename = f"{i:06d}.png"
            output_path = os.path.join(rgb_dir, new_filename)
            
            img = cv2.imread(original_path)
            if img is None: continue
                
            h, w = img.shape[:2]
            mask_h = int(h * MASK_RATIO)
            img[-mask_h:, :] = 0  # Black out bottom 14%
            
            cv2.imwrite(output_path, img)
            
            # Log real timestamp
            timestamp = parse_timestamp(original_path)
            f.write(f"{timestamp:.6f} rgb/{new_filename}\n")
            
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1}/{len(selected_images)} images...")

    print(f"Done! {len(selected_images)} masked images ready in {rgb_dir}")

if __name__ == "__main__":
    main()