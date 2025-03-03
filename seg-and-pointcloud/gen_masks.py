import os
import cv2
import numpy as np
import argparse

def generate_yolo_files_and_masks(image_folder, output_txt_folder, output_mask_folder, class_id):
    """
    Generate YOLO format labels and binary masks from images with alpha channels.

    Args:
        image_folder (str): Path to the folder containing input images.
        output_txt_folder (str): Path to save YOLO label files.
        output_mask_folder (str): Path to save binary mask images.
        class_id (int): Class ID for the YOLO labels.
    """
    # Create output folders if they don't exist
    os.makedirs(output_txt_folder, exist_ok=True)
    os.makedirs(output_mask_folder, exist_ok=True)

    for image_name in os.listdir(image_folder):
        if image_name.endswith((".png", ".jpg", ".jpeg")):
            # Load the image
            image_path = os.path.join(image_folder, image_name)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

            # Check if the image has an alpha channel
            if image.shape[-1] == 4:
                alpha_channel = image[:, :, 3]

                # Create a binary mask (object=white, background=black)
                mask = (alpha_channel > 0).astype(np.uint8) * 255
                mask_path = os.path.join(output_mask_folder, f"{os.path.splitext(image_name)[0]}_mask.png")
                cv2.imwrite(mask_path, mask)

                # Find contours from the alpha channel for YOLO bounding box
                contours, _ = cv2.findContours((alpha_channel > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    # Get bounding box
                    x, y, w, h = cv2.boundingRect(contours[0])
                    center_x = (x + w / 2) / image.shape[1]
                    center_y = (y + h / 2) / image.shape[0]
                    width = w / image.shape[1]
                    height = h / image.shape[0]

                    # Optional: Get segmentation mask points
                    segmentation = []
                    for point in contours[0]:
                        px, py = point[0]
                        segmentation.append(px / image.shape[1])
                        segmentation.append(py / image.shape[0])

                    # Write YOLO format file
                    txt_path = os.path.join(output_txt_folder, f"{os.path.splitext(image_name)[0]}.txt")
                    with open(txt_path, "w") as f:
                        # Write bounding box
                        f.write(f"{class_id} {center_x} {center_y} {width} {height}")
                        # Write segmentation mask if needed
                        if segmentation:
                            seg_str = " " + " ".join(map(str, segmentation))
                            f.write(seg_str)
                        f.write("\n")

    print("YOLO files and masks generated successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate YOLO labels and binary masks from images with alpha channels.")
    parser.add_argument("image_folder", type=str, help="Path to the folder containing input images.")
    parser.add_argument("output_txt_folder", type=str, help="Path to save YOLO label files.")
    parser.add_argument("output_mask_folder", type=str, help="Path to save binary mask images.")
    parser.add_argument("class_id", type=int, help="Class ID for the YOLO labels.")

    args = parser.parse_args()

    generate_yolo_files_and_masks(args.image_folder, args.output_txt_folder, args.output_mask_folder, args.class_id)
