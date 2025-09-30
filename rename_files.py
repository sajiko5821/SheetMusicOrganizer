import os
import re
import argparse

# ----------------------------------------------------------------------
# Define the mapping between the long name (found in file) and the 
# short name (used in new filename).
# NOTE: All keys in this dictionary are converted to lowercase in the script.
# ----------------------------------------------------------------------
DEFAULT_TARGET_MAP = {
    "trombone-1": "trb_1",
    "trombone-2": "trb_2",
    "trombone-3": "trb_3",
    "trombone-4": "trb_4",
    "trombone-set": "trb_set",
    # Add other mappings here if needed, e.g.,
    # "trumpet-1": "trp_1",
    # "violin-a": "vln_a",
}

def get_directory_name(directory_path):
    """
    Cleans and formats a directory name.
    """
    directory_name = os.path.basename(directory_path)
    directory_name = directory_name.lower()
    # Replace spaces, hyphens, and " - " with underscores
    directory_name = re.sub(r"[\s-]+", "_", directory_name)
    return directory_name

def rename_pdfs(root_directory, target_map, dry_run=False):
    """
    Renames PDF files in subdirectories based on specific patterns using a map.

    Args:
        root_directory (str): The path to the root directory.
        target_map (dict): A dictionary mapping filename substrings (keys) 
                           to the desired replacement short names (values).
        dry_run (bool, optional): If True, prints actions without performing them.
    """
    # Keys from the map are the strings we search for in the filename.
    # We sort them by length descending to ensure we match "trombone-set" 
    # before we might accidentally match "trombone".
    search_keys = sorted(target_map.keys(), key=len, reverse=True)

    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.lower().endswith(".pdf"):
                
                # Check each potential search key
                for search_key in search_keys:
                    
                    if search_key in filename.lower():
                        # Found a match!
                        
                        # The desired short name comes from the map's value
                        stimme_short_name = target_map[search_key] 
                        
                        # Get the cleaned directory name
                        directory_name = get_directory_name(dirpath)
                        
                        # Construct the new filename using the directory name and the SHORT name
                        new_filename = f"{directory_name}_{stimme_short_name}.pdf"
                        
                        # Construct the full paths
                        old_filepath = os.path.join(dirpath, filename)
                        new_filepath = os.path.join(dirpath, new_filename)
                        
                        # Skip if the file is already named correctly
                        if os.path.basename(old_filepath) == new_filename:
                            continue

                        if dry_run:
                            print(f"[DRY RUN] Renaming: {old_filepath} to {new_filepath}")
                        else:
                            try:
                                os.rename(old_filepath, new_filepath)
                                print(f"Renamed: {os.path.basename(old_filepath)} to {new_filename}")
                            except OSError as e:
                                print(f"Error renaming {old_filepath}: {e}")
                        
                        break  # Stop after finding and processing one match

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Rename PDF files in a directory tree.")
    parser.add_argument("root_dir", help="The root directory where the PDF files are located.")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Perform a dry run: print the renaming actions without actually renaming files.",
    )
    # NOTE: The '--targets' argument has been removed as we now use the fixed map.
    
    # Parse the arguments
    args = parser.parse_args()

    root_directory = args.root_dir
    dry_run = args.dry_run

    if not os.path.exists(root_directory):
        print(f"Error: The root directory '{root_directory}' does not exist.")
        exit(1)

    # Call the function with the fixed DEFAULT_TARGET_MAP
    rename_pdfs(root_directory, DEFAULT_TARGET_MAP, dry_run)