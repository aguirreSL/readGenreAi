import os
import subprocess
import time
import json
from .config import GENRES, GEMINI_AVAILABLE

if GEMINI_AVAILABLE:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel, Field

def classify_genre(song_title, use_gemini=False, model="llama3"):
    if use_gemini and GEMINI_AVAILABLE:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment. Falling back to Ollama.")
            use_gemini = False
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                class GenreResponse(BaseModel):
                    genre: str = Field(description="The exact genre name from the list provided.")
                    
                prompt = f"""
                Classify: "{song_title}.mp3" into one of these specific genres: 
                {', '.join(GENRES)}
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=GenreResponse,
                    ),
                )
                
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
    Classify: "{song_title}.mp3" from: {', '.join(GENRES)}</s> 
    <|assistant|>
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model, "--nowordwrap", prompt],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip()
        print(output)
        return output.split('\n')[-1].strip()
    except Exception as e:
        return "Unknown"

def classify_genre_batch(song_titles, use_gemini=False, model="deepseek-r1:8b"):
    if use_gemini and GEMINI_AVAILABLE:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment. Falling back to Ollama.")
            use_gemini = False
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                class GenreResponse(BaseModel):
                    filename: str = Field(description="The exact filename provided")
                    genre: str = Field(description="The exact genre name from the list provided")
                
                class BatchResponse(BaseModel):
                    results: list[GenreResponse]
                
                prompt = f"""
                Classify the electronic music genre/subgenre for the following song titles.
                Choose ONLY from this list: {', '.join(GENRES)}. 
                
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
                
                result_data = json.loads(response.text)
                genre_map = {}
                for item in result_data.get('results', []):
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
    Choose ONLY from this list: {', '.join(GENRES)}. 
    Return ONLY the genre name for each song. Do NOT add explanations.
    Return the results in this EXACT format:
    filename: genre

    Song titles:
    """ + "\n".join([f'"{title}"' for title in song_titles])

    try:
        result = subprocess.run(
            ["ollama", "run", model, "--verbose", prompt],
            capture_output=True, text=True, timeout=180
        )
        output = result.stdout.strip()
        genre_map = {}
        for line in output.split('\n'):
            if line.strip().startswith('"') and ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    filename = parts[0].strip().strip('"')
                    genre = parts[1].strip()
                    for song in song_titles:
                        if song == filename:
                            genre_map[song] = genre
                            break
        return genre_map
    except Exception as e:
        print(f"Batch classification error: {e}")
        return {title: "Unknown" for title in song_titles}

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

def process_batch_text(batch, use_gemini=False, retries=3, model="deepseek-r1:8b"):
    if use_gemini and GEMINI_AVAILABLE:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment. Falling back to Ollama.")
            use_gemini = False
        else:
            try:
                client = genai.Client(api_key=api_key)
                class GenreResponse(BaseModel):
                    filename: str = Field(description="The exact filename provided")
                    genre: str = Field(description="The exact genre name from the list provided")
                class BatchResponse(BaseModel):
                    results: list[GenreResponse]
                
                prompt = f"Classify electronic music tracks from this list: {', '.join(GENRES)}.\n\nTrack list:\n" + "\n".join(batch)
                
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
                        result_data = json.loads(response.text)
                        valid_lines = []
                        for item in result_data.get('results', []):
                            filename = item.get('filename', '').strip().strip('"')
                            genre = item.get('genre', 'Unknown').strip()
                            print(genre)
                            if genre in GENRES:
                                valid_lines.append(f"{filename}: {genre}")
                        return valid_lines or [f"{song.strip().strip('\"')}: Unknown" for song in batch]
                    except Exception as e:
                        print(f"Gemini API Batch Error (attempt {attempt+1}/{retries}): {e}")
                        time.sleep(2 ** attempt)
                return [f"{song.strip().strip('\"')}: Unknown" for song in batch]
            except Exception as e:
                print(f"Gemini API Error: {e}")
                return [f"{song.strip().strip('\"')}: Unknown" for song in batch]
                
    base_prompt = f"Classify electronic music tracks from this list: {', '.join(GENRES)}.\nReturn ONLY genre names in format: filename: genre"
    prompt = f"{base_prompt}\nTrack list:\n" + "\n".join(batch)
    
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True, text=True, timeout=180, check=True
            )
            return validate_output(result.stdout.strip(), batch)
        except subprocess.TimeoutExpired:
            print(f"Batch timeout (attempt {attempt+1}/{retries})")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Error: {e}")
    return []
