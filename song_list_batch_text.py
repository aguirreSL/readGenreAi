import time
from core.config import USE_GEMINI_API, GENRES
from core.utils import find_music_files, clean_filename
from core.classifier import process_batch_text

# Configuration
import os, sys
FOLDER_PATH = os.getenv('MUSIC_FOLDER_DEFAULT')
if not FOLDER_PATH:
    print('Error: Please set MUSIC_FOLDER_DEFAULT in your .env file.')
    sys.exit(1)
OUTPUT_FILE = './song_list.txt'
OUTPUT_FILE_WITH_GENRE = './song_list_with_genre_batch.txt'
BATCH_SIZE = 5

def main():
    music_files = find_music_files(FOLDER_PATH)
    song_titles = [clean_filename(f, FOLDER_PATH) for f in music_files]
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write("\n".join(song_titles))

    results = []
    batches = [song_titles[i:i+BATCH_SIZE] for i in range(0, len(song_titles), BATCH_SIZE)]
    
    for i, batch in enumerate(batches, 1):
        print(f"Processing batch {i}/{len(batches)} ({len(batch)} tracks)")
        batch_results = process_batch_text([f'"{title}"' for title in batch], use_gemini=USE_GEMINI_API)
        results.extend(batch_results)
        time.sleep(0.5)

    with open(OUTPUT_FILE_WITH_GENRE, 'w') as f:
        f.write("\n".join(results))

    print(f"Completed! Processed {len(song_titles)} tracks.")

if __name__ == "__main__":
    main()