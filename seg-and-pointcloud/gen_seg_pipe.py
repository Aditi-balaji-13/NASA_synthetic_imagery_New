import os
import cv2
import random
import time
import argparse
import numpy as np

def overlay_object_on_background(object_img, background_img):
    """
    Overlay an object with transparency onto a background image.

    Args:
        object_img (np.ndarray): Object image with an alpha channel.
        background_img (np.ndarray): Background image to overlay onto.

    Returns:
        np.ndarray: Composite image with the object overlaid on the background.
    """
    dimx, dimy, _ = object_img.shape
    for i in range(dimx):
        for j in range(dimy):
            if object_img[i, j, 3] == 0:  # Transparent pixel
                object_img[i, j, 0:3] = background_img[i % background_img.shape[0], j % background_img.shape[1], 0:3]
                object_img[i, j, 3] = 255  # Make it non-transparent
    return object_img


def generate_composite_images(args):
    """
    Generate composite images by overlaying objects on backgrounds and save corresponding masks.

    Args:
        args: Command-line arguments containing paths to input/output folders.
    """
    # Create output directories if they don't exist
    os.makedirs(args.output_images_folder, exist_ok=True)
    os.makedirs(args.output_masks_folder, exist_ok=True)

    # Get a list of files
    object_files = [f for f in os.listdir(args.objects_folder) if f.endswith((".png", ".jpg"))]
    mask_files = [f for f in os.listdir(args.masks_folder) if f.endswith(".txt")]
    background_files = [f for f in os.listdir(args.backgrounds_folder) if f.endswith((".jpg", ".png"))]

    # Check if object and mask lists are aligned
    assert len(object_files) == len(mask_files), "Mismatch between object and mask counts!"

    # Generate images
    start_time = time.time()
    for count in range(args.num_images):
        # Randomly select an object, its mask, and a background
        object_idx = random.randint(0, len(object_files) - 1)
        background_idx = random.randint(0, len(background_files) - 1)

        object_file = object_files[object_idx]
        mask_file = object_file.replace(".png", ".txt")
        background_file = background_files[background_idx]

        # Load object and background images
        object_img = cv2.imread(os.path.join(args.objects_folder, object_file), cv2.IMREAD_UNCHANGED)
        background_img = cv2.imread(os.path.join(args.backgrounds_folder, background_file), cv2.IMREAD_UNCHANGED)

        # Resize background to match object dimensions
        background_img = cv2.resize(background_img, (object_img.shape[1], object_img.shape[0]))

        # Overlay the object on the background
        composite_img = overlay_object_on_background(object_img.copy(), background_img)

        # Save the new image
        output_image_path = os.path.join(args.output_images_folder, f"image_{count + 1:05d}.png")
        cv2.imwrite(output_image_path, composite_img)

        # Copy the corresponding mask .txt file to the new folder
        output_mask_path = os.path.join(args.output_masks_folder, f"image_{count + 1:05d}.txt")
        with open(os.path.join(args.masks_folder, mask_file), 'r') as mask_file_content:
            mask_data = mask_file_content.read()
        with open(output_mask_path, 'w') as output_mask_file:
            output_mask_file.write(mask_data)

    end_time = time.time()
    print(f"Generated {args.num_images} images and masks in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate composite images by overlaying objects on backgrounds.")
    parser.add_argument("objects_folder", type=str, help="Path to the folder containing object images.")
    parser.add_argument("masks_folder", type=str, help="Path to the folder containing YOLO-style mask files.")
    parser.add_argument("backgrounds_folder", type=str, help="Path to the folder containing background images.")
    parser.add_argument("output_images_folder", type=str, help="Path to save composite images.")
    parser.add_argument("output_masks_folder", type=str, help="Path to save copied YOLO-style masks.")
    parser.add_argument("--num_images", type=int, default=10000, help="Number of images to generate.")

    args = parser.parse_args()
    generate_composite_images(args)
