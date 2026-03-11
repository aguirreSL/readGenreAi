import os
import time
from core.config import USE_GEMINI_API
from core.metadata import get_existing_genre, write_genre_to_metadata
from core.classifier import classify_genre

# Configuration
import sys
folder_path = os.getenv('MUSIC_FOLDER_ARCHIVED')
if not folder_path:
    print('Error: Please set MUSIC_FOLDER_ARCHIVED in your .env file.')
    sys.exit(1)
output_file = './song_list_with_genres_archived.txt'
files = [f for f in os.listdir(folder_path) 
         if os.path.isfile(os.path.join(folder_path, f)) 
         and not f.startswith('.')
         and not f.endswith('.txt')
         and not f.lower().endswith('.wav')
         and not f.lower().endswith('..serato-stems')]  # Exclude WAV files
total_files = len(files)
processed_files = 0

# First pass: Initial processing
with open(output_file, 'w') as file:
    for song in files:
        processed_files += 1
        song_path = os.path.join(folder_path, song)
        print(f"Processing {processed_files}/{total_files}: {song}...")
        
        # Check existing genre
        existing_genre = get_existing_genre(song_path)
        if existing_genre and existing_genre != "Other":
            print(f"Skipping {song} - existing genre: '{existing_genre}'")
            file.write(f"{song}: {existing_genre}\n")
            continue
            
        genre = classify_genre(song, use_gemini=USE_GEMINI_API)
        print(f"Predicted genre: {genre}")
        
        if write_genre_to_metadata(song_path, genre):
            print(f"Genre '{genre}' written to {song}")
            
        file.write(f"{song}: {genre}\n")
        time.sleep(1)

print("First pass completed. Checking for 'Other' results...")

def retry_unknowns(model):
    """Helper function for retrying 'Other' classifications"""
    with open(output_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        for line in lines:
            if ": " not in line:  # Skip malformed lines
                continue
                
            song, current_genre = line.strip().split(": ", 1)
            song_path = os.path.join(folder_path, song)
            
            existing_genre = get_existing_genre(song_path)
            if existing_genre and existing_genre != "Other":
                print(f"Using existing genre for {song}: '{existing_genre}'")
                file.write(f"{song}: {existing_genre}\n")
                continue
                
            if current_genre == "Other":
                print(f"Retrying with {model}: {song}...")
                new_genre = classify_genre(song, use_gemini=USE_GEMINI_API, model=model)
                if write_genre_to_metadata(song_path, new_genre):
                    print(f"Updated genre '{new_genre}' written to {song}")
                file.write(f"{song}: {new_genre}\n")
            else:
                file.write(line)

# Second pass with llama3
retry_unknowns("llama3")

print(f"Processing complete. Results saved to {output_file}")