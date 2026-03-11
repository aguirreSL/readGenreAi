**Read Me for Audio Genre Classification Script**

**Overview:**
This Python script automates the process of categorizing electronic music 
files into their respective genres based on their titles. It uses metadata 
from various audio formats (MP3, M4A, WAV) and employs an external model 
(either locally via the Ollama API or remotely via Google's Gemini API) 
to classify each file.

**Requirements:**
- **Audio Formats:** The script supports MP3, M4A, and WAV files.
- **External Model (Ollama):** An Ollama server with a compatible model 
  (e.g., `deepseek-r1:14b`, `llama3.1:8b`).
- **External Model (Gemini):** A Google Gemini API key is required. 
  It must be set as an environment variable (`GEMINI_API_KEY`) or in a `.env` file.
- **Imported Libraries:** Ensure the `mutagen`, `google-genai`, `python-dotenv`, 
  `os`, `subprocess`, and `time` libraries are installed (see `requirements.txt`).

**Configuration:**
- **Toggle Models:** You can switch between Gemini and Ollama by modifying 
  the `USE_GEMINI_API` variable in the script or via the `.env` file 
  (`USE_GEMINI_API=true` or `false`). Gemini is the default.
- **File Path:** Define where your music files are located inside the scripts.
- **Output File:** Specify the location for the output file containing 
  genre results.

**Workflow:**
1. **Process Each File:** The script processes each file in the specified 
directory, checking for existing metadata to avoid redundant processing.
2. **Classify Songs:** Files without an existing genre are classified 
using the Gemini API or Ollama API with specific models and subgenres 
of electronic music.
3. **Update Metadata:** The script updates the audio file's metadata with 
the classified genre, enhancing organization.
4. **Handle Unknowns:** Files initially marked as "Unknown" undergo 
retries with alternative models to improve accuracy.

**Features:**
- **Error Handling:** Robust error handling ensures smooth operation even 
with incompatible files.
- **Performance Optimization:** Includes a brief sleep period between 
iterations to prevent overwhelming the system.
- **Backup Results:** Creates a backup file of results, enabling 
subsequent passes to resolve 'Unknown' classifications.

**Why Use This Script?**
This script is ideal for organizing music collections by genre, updating 
metadata for better management, or automating categorization tasks for 
large datasets. It streamlines the process while leveraging external 
models for improved accuracy.