import os
import json
import re
import argparse

def get_directory_name(directory_path):
    """
    Gets the name of the directory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        str: The name of the directory.
    """
    return os.path.basename(directory_path)

def create_metadata_file(root_directory, dry_run=False):
    """
    Creates a metadata.json file in each directory containing PDF files.

    Args:
        root_directory (str): The path to the root directory.
        dry_run (bool, optional): If True, prints the actions without creating files.
            Defaults to False.
    """
    for dirpath, dirnames, filenames in os.walk(root_directory):
        has_pdf = any(filename.lower().endswith(".pdf") for filename in filenames)
        if has_pdf:
            # Construct the metadata dictionary
            directory_name = get_directory_name(dirpath) # Modified to use the original name
            metadata = {
                "Title": directory_name,
                "Author": "",
                "Subject": "",
                "Keywords": ["Skyline-BigBand"],
            }

            # Construct the full path to the metadata.json file
            metadata_filepath = os.path.join(dirpath, "metadata.json")

            if dry_run:
                print(f"[DRY RUN] Creating: {metadata_filepath} with content:")
                print(json.dumps(metadata, indent=4, ensure_ascii=False))
            else:
                # Write the metadata to the file
                try:
                    with open(metadata_filepath, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=4, ensure_ascii=False)
                    print(f"Created: {metadata_filepath}")
                except OSError as e:
                    print(f"Error creating {metadata_filepath}: {e}")
                except Exception as e:
                    print(f"Error writing JSON to {metadata_filepath}: {e}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Create metadata.json files in directories containing PDF files.")
    parser.add_argument("root_dir", help="The root directory where the directories are located.")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Perform a dry run: print the creation actions without actually creating files.",
    )
    args = parser.parse_args()

    # Get the root directory from the arguments
    root_directory = args.root_dir

    # Get the dry-run flag
    dry_run = args.dry_run

    # Check if the root directory exists
    if not os.path.exists(root_directory):
        print(f"Error: The root directory '{root_directory}' does not exist.")
        exit(1)  # Exit with an error code

    # Call the function to create the metadata files
    create_metadata_file(root_directory, dry_run)
