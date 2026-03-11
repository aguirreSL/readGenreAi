import os
import subprocess
import time
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE

# Try to import Gemini modules
try:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel, Field
    import json
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    
from dotenv import load_dotenv
load_dotenv()

def write_genre_to_metadata(file_path, genre):
    try:
        if file_path.lower().endswith('.mp3'):
            audio = EasyID3(file_path)
            audio['genre'] = genre
            audio.save()
        elif file_path.lower().endswith('.m4a'):
            audio = MP4(file_path)
            audio['\xa9gen'] = genre
            audio.save()
        elif file_path.lower().endswith('.wav'):
            audio = WAVE(file_path)
            audio['genre'] = genre
            audio.save()
        else:
            print(f"Unsupported file format: {file_path}")
        return True
    except Exception as e:
        print(f"Error writing metadata to {file_path}: {e}")
        return False

def classify_genre_batch(song_titles, USE_GEMINI=False, model="deepseek-r1:8b"):
    if USE_GEMINI and GEMINI_AVAILABLE:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment. Falling back to Ollama.")
            USE_GEMINI = False
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # Use Structured Outputs to guarantee exact genre names map
                class GenreResponse(BaseModel):
                    filename: str = Field(description="The exact filename provided")
                    genre: str = Field(description="The exact genre name from the list provided")
                
                class BatchResponse(BaseModel):
                    results: list[GenreResponse]
                
                prompt = f"""
                Classify the electronic music genre/subgenre for the following song titles.
                Choose ONLY from this list: House, Deep House, Tech House, Electro House, Deep Techno, Drum and Bass, Trance, Progressive Trance, Psytrance, Techno, Acid Techno, Minimal Techno, Hard Techno, Electro, Nu-Disco. 
                
                Song titles:
                """ + "\n".join([f'"{title}"' for title in song_titles])
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=BatchResponse,
                    ),
                )
                
                # Parse JSON
                result_data = json.loads(response.text)
                genre_map = {}
                for item in result_data.get('results', []):
                    # Match filenames exactly
                    filename = item.get('filename', '').strip().strip('"')
                    genre = item.get('genre', 'Unknown').strip()
                    for song in song_titles:
                        if song == filename:
                            genre_map[song] = genre
                            break
                return genre_map
            except Exception as e:
                print(f"Gemini API Batch Error: {e}")
                return {title: "Unknown" for title in song_titles}

    # Fallback / Default: Ollama
    prompt = f"""
    Classify the electronic music genre/subgenre for the following song titles.
    Choose ONLY from this list: House, Deep House, Tech House, Electro House, Deep Techno, Drum and Bass, Trance, Progressive Trance, Psytrance, Techno, Acid Techno, Minimal Techno, Hard Techno, Electro, Nu-Disco. 
    Return ONLY the genre name for each song. Do NOT add explanations.
    Return the results in this EXACT format:
    filename: genre

    Song titles:
    """ + "\n".join([f'"{title}"' for title in song_titles])

    try:
        # Run the model
        # print(subprocess.run(
        #     ["ollama", "list"]))
        result = subprocess.run(
            ["ollama", "run", model, "--verbose", prompt],
            capture_output=True, text=True, timeout=180
        )
        output = result.stdout.strip()

        # Debug: Print the raw output for inspection
        # print("Model output:")
        # print(output)

        # Parse the response
        genre_map = {}
        for line in output.split('\n'):
            if line.strip().startswith('"') and ":" in line:
                # Extract the filename and genre
                parts = line.split(":", 1)
                if len(parts) == 2:
                    filename = parts[0].strip().strip('"')  # Remove quotes
                    genre = parts[1].strip()
                    # Match the filename to the actual song title in the batch
                    for song in song_titles:
                        if song == filename:
                            genre_map[song] = genre
                            break
        return genre_map
    except Exception as e:
        print(f"Batch classification error: {e}")
        return {title: "Unknown" for title in song_titles}

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Main script
# Configuration
USE_GEMINI_API = os.getenv("USE_GEMINI_API", "true").lower() == "true"
if USE_GEMINI_API and not GEMINI_AVAILABLE:
    print("Warning: python-dotenv and google-genai needed for Gemini API. Using Ollama.")

# folder_path = '/Users/lilian/Music/Eletronic/'
folder_path = '/Users/sergioaguirre/Music/Iceberg-Storage/Playlist_Beatport/Melodic_House'
# Filter out non-song files
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.') and not f.endswith('.txt')]
output_file = os.path.join(folder_path, 'song_list_with_genres_batch.txt')

# First pass: Use the smaller model (deepseek-r1:8b) in batches
with open(output_file, 'w') as file:
    for batch in chunks(files, 3):  # Process in batches of 5
        print(f"\nProcessing batch of {len(batch)} songs:")
        print("-" * 40)
        
        # Get predictions for the whole batch
        genre_map = classify_genre_batch(batch, USE_GEMINI=USE_GEMINI_API)
        
        for song in batch:
            song_path = os.path.join(folder_path, song)
            genre = genre_map.get(song, "Unknown")
            
            # Write metadata and file entry
            success = write_genre_to_metadata(song_path, genre)
            file.write(f"{song}: {genre}\n")
            print(f"{song} -> {genre} {'(Written)' if success else '(Failed)'}")
        
        time.sleep(2)  # Reduced delay for batch processing

print("First pass completed. Checking for 'Unknown' results...")

# Second pass: Retry with a Different model (llama3.1:8b) for "Unknown" results
# with open(output_file, 'r') as file:
#     lines = file.readlines()

# # Collect songs with "Unknown" genre
# unknown_songs = []
# for line in lines:
#     song, genre = line.strip().split(": ")
#     if genre == "Unknown":
#         unknown_songs.append(song)

# # Retry with a larger model in batches
# if unknown_songs:
#     print(f"\nRetrying {len(unknown_songs)} 'Unknown' songs with a larger model...")
#     for batch in chunks(unknown_songs, 5):  # Process in batches of 5
#         print(f"\nProcessing batch of {len(batch)} 'Unknown' songs:")
#         print("-" * 40)
        
#         # Get predictions for the whole batch
#         genre_map = classify_genre_batch(batch, model="llama3.1:8b")
        
#         for song in batch:
#             song_path = os.path.join(folder_path, song)
#             genre = genre_map.get(song, "Unknown")
            
#             # Write metadata and file entry
#             success = write_genre_to_metadata(song_path, genre)
#             print(f"{song} -> {genre} {'(Written)' if success else '(Failed)'}")
        
#         time.sleep(2)  # Reduced delay for batch processing

# # Third pass: Retry with a larger model (deepseek-r1:14b) for remaining "Unknown" results
# with open(output_file, 'r') as file:
#     lines = file.readlines()

# # Collect remaining songs with "Unknown" genre
# unknown_songs = []
# for line in lines:
#     song, genre = line.strip().split(": ")
#     if genre == "Unknown":
#         unknown_songs.append(song)

# # Retry with a larger model in batches
# if unknown_songs:
#     print(f"\nRetrying {len(unknown_songs)} remaining 'Unknown' songs with a larger model...")
#     for batch in chunks(unknown_songs, 5):  # Process in batches of 5
#         print(f"\nProcessing batch of {len(batch)} 'Unknown' songs:")
#         print("-" * 40)
        
#         # Get predictions for the whole batch
#         genre_map = classify_genre_batch(batch, model="deepseek-r1:14b")
        
#         for song in batch:
#             song_path = os.path.join(folder_path, song)
#             genre = genre_map.get(song, "Unknown")
            
#             # Write metadata and file entry
#             success = write_genre_to_metadata(song_path, genre)
#             print(f"{song} -> {genre} {'(Written)' if success else '(Failed)'}")
        
#         time.sleep(2)  # Reduced delay for batch processing

print(f"List saved to {output_file}")