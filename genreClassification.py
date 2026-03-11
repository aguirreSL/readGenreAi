import os
import subprocess
import time
from mutagen.easyid3 import EasyID3  # For MP3 files
from mutagen.mp4 import MP4          # For M4A files
from mutagen.wave import WAVE        # For WAV files
from mutagen import File
from mutagen.id3 import ID3, TCON    # For WAV files with ID3 tags (if applicable)

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


def get_existing_genre(file_path):
    """Read existing genre from file metadata"""
    try:
        if file_path.lower().endswith('.mp3'):
            audio = EasyID3(file_path)
            return audio.get('genre', [''])[0]
        elif file_path.lower().endswith('.m4a'):
            audio = MP4(file_path)
            return audio.get('\xa9gen', [''])[0]
        elif file_path.lower().endswith('.wav'):
            # Handle WAV files using the WAVE class
            audio = WAVE(file_path)
            if 'genre' in audio.tags:
                return audio.tags['genre'][0]
            return ''
        else:
            return ''
    except Exception as e:
        print(f"Error reading metadata from {file_path}: {e}")
        return ''

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
            # Handle WAV files using the WAVE class
            audio = WAVE(file_path)
            audio.tags['genre'] = genre
            audio.save()
        else:
            print(f"Unsupported file format: {file_path}")
        return True
    except Exception as e:
        print(f"Error writing metadata to {file_path}: {e}")
        return False

def classify_genre(song_title, USE_GEMINI=False, model="llama3"):
    if USE_GEMINI and GEMINI_AVAILABLE:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment. Falling back to Ollama.")
            USE_GEMINI = False
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # Use Structured Outputs to guarantee exact genre names
                class GenreResponse(BaseModel):
                    genre: str = Field(description="The exact genre name from the list provided.")
                    
                prompt = f"""
                Classify: "{song_title}.mp3" into one of these specific genres: 
                House, Deep House, Tech House, Electro House, Deep Techno, Drum and Bass, Trance, Progressive Trance, Psytrance, Techno, Acid Techno, Minimal Techno, Hard Techno, Electro, Nu-Disco.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=GenreResponse,
                    ),
                )
                
                # Parse JSON string back into a dict/object to get the raw genre
                result = json.loads(response.text)
                genre = result.get('genre', 'Unknown')
                print(f"Gemini output: {genre}")
                return genre
            except Exception as e:
                print(f"Gemini API Error: {e}")
                return "Unknown"
                
    # Fallback / Default: Ollama
    prompt = f"""
    <|system|>
    You are a music genre classifier. Respond ONLY with the exact genre name from the provided list.
    No explanations, no XML tags, no thinking process.</s>
    <|user|>
    Classify: "{song_title}.mp3" from: House, Deep House, Tech House, Electro House, Deep Techno, Drum and Bass, Trance, Progressive Trance, Psytrance, Techno, Acid Techno, Minimal Techno, Hard Techno, Electro, Nu-Disco</s> 
    <|assistant|>
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model,
             "--nowordwrap",
             prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        # Clean output using last line fallback
        output = result.stdout.strip()
        print(output)
        return output.split('\n')[-1].strip()
    except Exception as e:
        return "Unknown"

# Configuration
USE_GEMINI_API = os.getenv("USE_GEMINI_API", "true").lower() == "true"
if USE_GEMINI_API and not GEMINI_AVAILABLE:
    print("Warning: python-dotenv and google-genai needed for Gemini API. Using Ollama.")
folder_path = '/Users/sergioaguirre/Music/Iceberg-Storage/DJSoftware/Archived'
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
        if existing_genre and existing_genre != "Other":  # Skip only if genre exists and is not "Other"
            print(f"Skipping {song} - existing genre: '{existing_genre}'")
            file.write(f"{song}: {existing_genre}\n")
            continue
            
        genre = classify_genre(song, USE_GEMINI_API)
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
            
            # Check if genre exists in metadata and isn't "Other"
            existing_genre = get_existing_genre(song_path)
            if existing_genre and existing_genre != "Other":  # Skip if genre exists and is not "Other"
                print(f"Using existing genre for {song}: '{existing_genre}'")
                file.write(f"{song}: {existing_genre}\n")
                continue
                
            if current_genre == "Other":
                print(f"Retrying with {model}: {song}...")
                new_genre = classify_genre(song, USE_GEMINI_API, model)
                if write_genre_to_metadata(song_path, new_genre):
                    print(f"Updated genre '{new_genre}' written to {song}")
                file.write(f"{song}: {new_genre}\n")
            else:
                file.write(line)

# Second pass with llama3.1:8b
retry_unknowns("llama3")

# Third pass with deepseek-r1:14b (optional)
# retry_unknowns("deepseek-r1:14b")

print(f"Processing complete. Results saved to {output_file}")