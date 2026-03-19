import os
import json
import re
import argparse
import pikepdf  # Import the pikepdf library

def get_stimme_from_filename(filename):
    """
    Extracts the "stimme" (voice part) from a PDF filename.

    Args:
        filename (str): The name of the PDF file.

    Returns:
        str: The "stimme" (e.g., "trb_1", "trb_2"), or None if not found.
    """
    target_strings = ["trb_1", "trb_2", "trb_3", "trb_4", "trb_set"]
    for target in target_strings:
        if target in filename.lower():
            return target
    return None

def add_metadata_to_pdf(root_directory, dry_run=False):
    """
    Adds metadata to PDF files based on corresponding metadata.json files.

    Args:
        root_directory (str): The path to the root directory.
        dry_run (bool, optional): If True, prints the actions without modifying files.
            Defaults to False.
    """
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.lower().endswith(".pdf"):
                pdf_filepath = os.path.join(dirpath, filename)
                metadata_filepath = os.path.join(dirpath, "metadata.json")

                if os.path.exists(metadata_filepath):
                    try:
                        with open(metadata_filepath, "r", encoding="utf-8") as f:
                            metadata_json = json.load(f)
                        # Construct the title.
                        stimme = get_stimme_from_filename(filename)
                        if stimme:
                            pdf_title = f"{metadata_json['Title']} - {stimme}"
                            # Add stimme to keywords
                            keywords = metadata_json.get("Keywords", [])  # get existing keywords or empty list
                            if stimme not in keywords:
                                keywords.append(stimme)
                        else:
                            pdf_title = metadata_json['Title']
                            keywords = metadata_json.get("Keywords", [])
                        if dry_run:
                            print(f"[DRY RUN] Adding metadata to: {pdf_filepath} with title: {pdf_title}")
                            print(f"[DRY RUN]   Author: {metadata_json.get('Author', '')}")
                            print(f"[DRY RUN]   Subject: {metadata_json.get('Subject', '')}")
                            print(f"[DRY RUN]   Keywords: {', '.join(keywords)}")
                        else:
                            # Open the PDF with allow_overwriting_input=True
                            pdf = pikepdf.Pdf.open(pdf_filepath, allow_overwriting_input=True)
                            pdf.docinfo["/Title"] = pikepdf.String(pdf_title)
                            pdf.docinfo["/Author"] = pikepdf.String(metadata_json.get("Author", ""))
                            pdf.docinfo["/Subject"] = pikepdf.String(metadata_json.get("Subject", ""))
                            pdf.docinfo["/Keywords"] = pikepdf.String(", ".join(keywords))

                            pdf.save(pdf_filepath)
                            pdf.close()
                            print(f"Added metadata to: {pdf_filepath}")

                    except (OSError, pikepdf.PdfError) as e:
                        print(f"Error processing {pdf_filepath}: {e}")
                    except KeyError as e:
                        print(f"Error: Missing key in {metadata_filepath}: {e}")
                else:
                    print(f"Warning: No metadata.json found for {pdf_filepath}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Add metadata to PDF files based on metadata.json files.")
    parser.add_argument("root_dir", help="The root directory where the PDF and metadata.json files are located.")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Perform a dry run: print the actions without modifying files.",
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

    # Call the function to add metadata to the PDFs
    add_metadata_to_pdf(root_directory, dry_run)
