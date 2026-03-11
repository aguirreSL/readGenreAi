import os
import subprocess

prompt = f"""
    Classify the electronic music genre/subgenre for the song title below.
    Choose ONLY from this list: Techno, House, Trance, Dubstep, Drum and Bass, Ambient, Hardstyle, Electro, Synthwave, Future Bass, Progressive House, Deep House, Tech House, Breakbeat, Chillout, Downtempo, Glitch Hop, IDM, UK Garage.
    Return ONLY the genre name. Do NOT add explanations.
    Song title: "Black Science Orchestra - Save Us (Motorcitysoul remix).mp3"
    """

# Run Ollama with the prompt
result = subprocess.run(
    ["ollama", "run", "deepseek-r1:8b", "--verbose", prompt],
    capture_output=True, text=True
)

# Extract the genre from the output
output = result.stdout.strip()

# Remove <think> tags and any extra text
if "<think>" in output:
    # Split the output into parts and extract the last part (the genre)
    genre = output.split("\n\n")[-1].strip()
else:
    genre = output.strip()

# Print the final genre
print(genre)