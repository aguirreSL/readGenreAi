import os
import fnmatch
import subprocess
import time
from pathlib import Path

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

# Configuration
FOLDER_PATH = '/Volumes/music/DJSoftware/Archived Songs/'
OUTPUT_FILE = './song_list.txt'
OUTPUT_FILE_WITH_GENRE = './song_list_with_genre_batch.txt'
MUSIC_EXTENSIONS = ['*.mp3', '*.wav', '*.flac', '*.aac', '*.ogg', '*.m4a']
BATCH_SIZE = 5
MODEL_NAME = "deepseek-r1:8b"  # Replace with your model
GENRES = [
    "House", "Deep House", "Progressive House", "Tech House", "Electro House",
    "Deep Techno", "Acid House", "Disco House", "Drum and Bass", "Trance",
    "Progressive Trance", "Psytrance", "Techno", "Acid Techno", "Minimal Techno",
    "Hard Techno", "Electro", "Nu-Disco"
]

def find_music_files(directory):
    music_files = []
    for root, _, files in os.walk(directory):
        for ext in MUSIC_EXTENSIONS:
            for f in fnmatch.filter(files, ext):
                music_files.append(Path(root) / f)
    return music_files

def clean_filename(path):
    return path.relative_to(FOLDER_PATH).with_suffix('').as_posix()

def process_batch(batch, USE_GEMINI=False, retries=3):
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
                
                prompt = f"""Classify electronic music tracks from this list: {', '.join(GENRES)}.
                
                Track list:
                """ + "\n".join(batch)
                
                for attempt in range(retries):
                    try:
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
                        
                        valid_lines = []
                        for item in result_data.get('results', []):
                            # Remove surrounding quotes from filename if present
                            filename = item.get('filename', '').strip().strip('"')
                            genre = item.get('genre', 'Unknown').strip()
                            print(genre)
                            
                            # Validate
                            if genre in GENRES:
                                # Compare against our original batch which has quotes
                                # (the logic above passes quoted strings as batch items)
                                # So if input filename is "foo", item['filename'] might be foo or "foo"
                                valid_lines.append(f"{filename}: {genre}")
                        
                        return valid_lines or [f"{song.strip().strip('\"')}: Unknown" for song in batch]
                        
                    except Exception as e:
                        print(f"Gemini API Batch Error (attempt {attempt+1}/{retries}): {e}")
                        time.sleep(2 ** attempt)
                        
                return [f"{song.strip().strip('\"')}: Unknown" for song in batch]
            except Exception as e:
                print(f"Gemini API Error: {e}")
                return [f"{song.strip().strip('\"')}: Unknown" for song in batch]
                
    # Fallback / Default: Ollama
    base_prompt = f"""Classify electronic music tracks from this list: {', '.join(GENRES)}.
Return ONLY genre names in format: filename: genre"""
    
    prompt = f"{base_prompt}\nTrack list:\n" + "\n".join(batch)
    
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["ollama", "run", MODEL_NAME, prompt],
                capture_output=True, 
                text=True, 
                timeout=180,
                check=True
            )
            return validate_output(result.stdout.strip(), batch)
        except subprocess.TimeoutExpired:
            print(f"Batch timeout (attempt {attempt+1}/{retries})")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(f"Error: {e}")
    return []

def validate_output(output, batch):
    valid_lines = []
    for line in output.split('\n'):
        if ':' in line:
            filename, _, genre = line.partition(':')
            genre = genre.strip()
            print(genre)
            if genre in GENRES:
                valid_lines.append(f"{filename.strip()}: {genre}")
    return valid_lines or [f"{song}: Unknown" for song in batch]

def main():
    # Get and clean song titles
    music_files = find_music_files(FOLDER_PATH)
    song_titles = [clean_filename(f) for f in music_files]
    
    # Write clean list
    with open(OUTPUT_FILE, 'w') as f:
        f.write("\n".join(song_titles))

    # Process in batches
    results = []
    batches = [song_titles[i:i+BATCH_SIZE] for i in range(0, len(song_titles), BATCH_SIZE)]
    
    for i, batch in enumerate(batches, 1):
        print(f"Processing batch {i}/{len(batches)} ({len(batch)} tracks)")
        batch_results = process_batch([f'"{title}"' for title in batch], USE_GEMINI=USE_GEMINI_API)
        results.extend(batch_results)
        time.sleep(0.5)  # Rate limiting

    # Write final output
    with open(OUTPUT_FILE_WITH_GENRE, 'w') as f:
        f.write("\n".join(results))

    print(f"Completed! Processed {len(song_titles)} tracks.")

if __name__ == "__main__":
    main()