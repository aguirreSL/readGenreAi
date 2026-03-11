# readGenreAI - Repository Analysis Report

## Overview
`readGenreAI` is a Python-based utility repository designed primarily to automate the categorization and organization of electronic music files. By leveraging Large Language Models (LLMs) via either **Google's Gemini API** or locally via **Ollama**, the core scripts analyze song titles and intelligently classify them into specific electronic music subgenres. 

The repository also includes metadata modification utilities to write these predicted genres directly into the audio files (MP3, M4A, WAV), alongside scripts for finding duplicate files and managing large music library lists.

---

## Core Capabilities

1. **AI-Powered Genre Classification**: 
   Predicts specific electronic subgenres (e.g., Deep House, Progressive Trance, Acid Techno) based purely on song filenames using either local LLM models (like `llama3.1:8b` or `deepseek-r1:8b`) or the remote **Gemini API** (`gemini-2.5-flash`) by securely utilizing structured outputs to guarantee precise genre formatting.
   
2. **Metadata Tagging**: 
   Reads existing metadata and writes newly predicted genres seamlessly back into the standard metadata tags (ID3 for MP3, Apple formats for M4A, and WAVE/RIFF tags for WAV).

3. **Performance & Batch Processing**: 
   Large numbers of files can be processed in grouped batches for efficiency, significantly reducing processing time and API overhead compared to processing one-by-one.

4. **Multi-Pass Retry System**: 
   Songs that receive an "Unknown" or "Other" classification in a first pass can automatically be retried using larger, more complex LLM models (e.g., `deepseek-r1:14b`) to improve classification accuracy.

5. **Utility Tools**:
   Includes general system utilities for deduplication and library indexing (SHA-256 hash checking and recursive directory listing).

---

## File Breakdown

### Main Classification Scripts
- **`genreClassification.py`**: 
  The primary, single-file processing script. It recursively scans directory files, checks for existing genres to avoid redundant API queries, classifies the track using `ollama`, and injects the result into the song's metadata tags. Handles multi-pass error correction directly.
  
- **`genreClassification_batch.py`**: 
  An optimized version of the classifier that processes chunked batches of songs simultaneously (e.g., 5 songs per prompt). Designed to increase throughput for larger folders. Includes fallback logic to retry failed classifications.

- **`song_list_batch_text.py`**: 
  A modern iteration of the batch processor that explicitly validates LLM outputs against an accepted list of 18 specific electronic genres. Includes exponential backoff for timeout handling and writes mapped genres to a text file rather than modifying the audio directly.

### Operational Utilities
- **`list_music_files.py`**: 
  Sequentially targets a root folder and writes all relative paths of recognized music file extensions (mp3, wav, flac, aac, m4a, ogg) to an output text document (`song_list.txt`).

- **`find_duplicates.py`**: 
  A file de-duplication script that recursively scans a target directory. It groups files matching by identical SHA-256 content hashes (reading data in chunks for memory safety) and exports a textual report mapping hashes to identical file paths.

### Auxiliary Files
- **`readme.txt`**: 
  Documentation covering the requirements, workflow, and basic feature list of the genre classifier.
- **`requirements.txt`**: 
  A robust list of Python dependencies. Notably contains ML/data science libraries (`tensorflow`, `scikit-learn`, `librosa`), metadata modules (`mutagen`), and API modules (`ollama`, `requests`), hinting at experimental audio analysis elements.

---

## Setup & Workflow Prerequisites

To utilize the core classification scripts inside this repository, the following environment is required:
1. **Python 3.x** and listed dependencies in `requirements.txt` (crucially `mutagen` for metadata injection and `google-genai` for API connection).
2. **Environment Variables**: To use the Gemini API (default setup), you must define `GEMINI_API_KEY` in your environment or via a `.env` file at the root of the repository. You can toggle back to using local models by setting `USE_GEMINI_API=false`.
3. **[Ollama](https://ollama.com/) (Optional)**: If you disable Gemini, the scripts fall back to requiring an active Ollama service runtime, loaded with the models specified in the code.
4. **Configuration**: Target folder paths are hardcoded within the main scripts (e.g., `/Volumes/music/...`). Users need to configure these paths to point to their own directories before execution.

---

## Summary
`readGenreAI` solves the common problem of organizing massive, unstructured electronic music libraries. By reading file names and passing them to an LLM, the repository dynamically resolves the track's genre and bakes it into the permanent metadata of the file, providing a more structured and sortable music library for DJ software and media players.
