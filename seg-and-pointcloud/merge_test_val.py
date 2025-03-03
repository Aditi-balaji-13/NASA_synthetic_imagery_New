import os
import shutil
import argparse

def merge_datasets_into_val(val_image_folder, val_label_folder, test_image_folder, test_label_folder):
    """
    Merges test images and masks into the validation dataset folders sequentially.

    Args:
        val_image_folder (str): Path to the validation images folder.
        val_label_folder (str): Path to the validation masks folder (labels).
        test_image_folder (str): Path to the test images folder.
        test_label_folder (str): Path to the test masks folder (labels).

    Output:
        - All images and masks from test are merged into the `val` folder structure.
    """

    # Helper function to rename and copy files
    def rename_and_copy(source_folder, destination_folder, start_index, prefix):
        index = start_index
        for filename in sorted(os.listdir(source_folder)):
            # Only process relevant file types
            if filename.endswith((".png", ".jpg", ".jpeg", ".txt")):  # Adjust as needed
                ext = os.path.splitext(filename)[-1]
                new_name = f"{prefix}_{index:05d}{ext}"
                shutil.copy(os.path.join(source_folder, filename), os.path.join(destination_folder, new_name))
                index += 1
        return index

    # Get the current highest index in the validation folders
    val_images = sorted(os.listdir(val_image_folder))
    val_labels = sorted(os.listdir(val_label_folder))

    # Calculate the starting index for new files
    current_max_index = 1
    if val_images:
        current_max_index = int(os.path.splitext(val_images[-1])[0].split("_")[-1]) + 1

    # Process test images
    next_index = rename_and_copy(test_image_folder, val_image_folder, current_max_index, "image")

    # Process test masks (labels)
    rename_and_copy(test_label_folder, val_label_folder, current_max_index, "mask")

    print(f"Merging complete! Images and masks merged into: {val_image_folder} and {val_label_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge test dataset into validation dataset folders.")
    parser.add_argument("--val_image_folder", type=str, required=True, help="Path to validation images folder")
    parser.add_argument("--val_label_folder", type=str, required=True, help="Path to validation labels folder")
    parser.add_argument("--test_image_folder", type=str, required=True, help="Path to test images folder")
    parser.add_argument("--test_label_folder", type=str, required=True, help="Path to test labels folder")
    
    args = parser.parse_args()
    
    merge_datasets_into_val(
        args.val_image_folder,
        args.val_label_folder,
        args.test_image_folder,
        args.test_label_folder
    )
