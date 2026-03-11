import os
import time
from core.config import USE_GEMINI_API
from core.metadata import write_genre_to_metadata
from core.classifier import classify_genre_batch
from core.utils import chunks

# Configuration
import sys
folder_path = os.getenv('MUSIC_FOLDER_BEATPORT')
if not folder_path:
    print('Error: Please set MUSIC_FOLDER_BEATPORT in your .env file.')
    sys.exit(1)
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.') and not f.endswith('.txt')]
output_file = os.path.join(folder_path, 'song_list_with_genres_batch.txt')

with open(output_file, 'w') as file:
    for batch in chunks(files, 3):
        print(f"\nProcessing batch of {len(batch)} songs:")
        print("-" * 40)
        
        genre_map = classify_genre_batch(batch, use_gemini=USE_GEMINI_API)
        
        for song in batch:
            song_path = os.path.join(folder_path, song)
            genre = genre_map.get(song, "Unknown")
            
            # Write metadata and file entry
            success = write_genre_to_metadata(song_path, genre)
            file.write(f"{song}: {genre}\n")
            print(f"{song} -> {genre} {'(Written)' if success else '(Failed)'}")
        
        time.sleep(2)  # Delay for batch processing

print("Batch processing complete.")
print(f"List saved to {output_file}")