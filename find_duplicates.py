import os
import hashlib
from collections import defaultdict

def calculate_file_hash(filepath, hash_algorithm="sha256", chunk_size=8192):
    """Calculate the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(hash_algorithm)
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except (IOError, OSError) as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def find_duplicates(directory, hash_algorithm="sha256"):
    """Find duplicate files in a directory based on their content."""
    hashes = defaultdict(list)
    
    for root, _, files in os.walk(directory):
        for file in files:
            # Skip hidden files (e.g., .DS_Store)
            if file.startswith("."):
                print(f"Skipping hidden file: {file}")  # Debugging
                continue
            
            filepath = os.path.join(root, file)
            print(f"Processing file: {filepath}")  # Debugging: Print each file being processed
            file_hash = calculate_file_hash(filepath, hash_algorithm)
            if file_hash:
                hashes[file_hash].append(filepath)
    
    # Filter out hashes with only one file (no duplicates)
    duplicates = {hash_val: paths for hash_val, paths in hashes.items() if len(paths) > 1}
    return duplicates

def export_duplicates_to_file(duplicates, output_file):
    """Export the list of duplicates to a file."""
    with open(output_file, "w") as f:
        for hash_val, files in duplicates.items():
            f.write(f"Duplicate files with hash {hash_val}:\n")
            for file in files:
                f.write(f"  - {file}\n")
            f.write("\n")

def main():
    # Define the directory to check
    directory = "/Volumes/photo/"  # Directory to verify for duplicates
    
    # Find duplicates in the directory
    print(f"Finding duplicates in: {directory}")
    duplicates = find_duplicates(directory)
    
    # Export duplicates to a file
    output_file = "duplicates_report.txt"
    export_duplicates_to_file(duplicates, output_file)
    print(f"\nDuplicate report saved to: {output_file}")

if __name__ == "__main__":
    main()