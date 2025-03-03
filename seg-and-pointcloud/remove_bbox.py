import os
import argparse

def remove_bbox_info(folder_path):
    """
    Removes bounding box information from YOLO format files, keeping only label_id and mask information.

    Args:
        folder_path (str): Path to the folder containing YOLO annotation files.

    Returns:
        None
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            updated_lines = []

            with open(file_path, "r") as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) > 5:  # Ensure there is mask information
                        # Keep label_id and mask information (remove bbox)
                        updated_line = f"{parts[0]} " + " ".join(parts[5:])
                        updated_lines.append(updated_line)
                    else:
                        print(f"Skipping file {file_name} due to insufficient data on line: {line.strip()}")

            # Write the updated content back to the file
            with open(file_path, "w") as file:
                file.write("\n".join(updated_lines) + "\n")

    print("Bounding box information removed from all files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove bounding box information from YOLO annotation files.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing YOLO annotation files.")
    args = parser.parse_args()

    remove_bbox_info(args.folder_path)
