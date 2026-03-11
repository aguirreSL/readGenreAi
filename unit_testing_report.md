# readGenreAI - Unit Testing Report

## Overview
The `readGenreAI` testing suite isolates and algorithmically verifies the shared logic from the `core/` package without depending on physical audio files, live network queries, or local Ollama servers. It achieves this by heavily relying on the Python `unittest.mock` library to simulate external dependencies.

To run the test suite, navigate to the repository root and execute:
```bash
python -m unittest discover tests
```

---

## Test Breakdowns

### 1. `test_metadata.py`
These tests ensure the utility functions capable of reading and injecting subgenres into actual `.mp3` / `.wav` audio files function as expected.

- **`test_get_existing_genre_mp3`**:
  - **Mocks**: Validates the metadata reader by intercepting calls to `EasyID3` from the `mutagen` package.
  - **Verifies**: Ensures that when an MP3 is loaded, our script successfully isolates and returns the first genre string tag from its internal list format (e.g. `['House']` -> `"House"`).
  
- **`test_write_genre_to_metadata_mp3`**:
  - **Mocks**: The `EasyID3` object's read and `save()` operations.
  - **Verifies**: Proves that string data input into our core functions correctly mutates the `genre` dictionary element of the Mutagen ID3 object, and critically verifies that `save()` is subsequently invoked.

- **`test_write_genre_error_handling`**:
  - **Mocks**: Forces `EasyID3` to throw an artificial `Exception` (simulating file permission/lock errors).
  - **Verifies**: Ensures the overarching application does not crash when hitting corrupted or locked files, predictably catching the exception and returning a `False` boolean state instead.

### 2. `test_classifier.py`
These tests validate the heart of the logic: the routing system that switches between asking the local Ollama subprocess, or contacting the Google Gemini API securely.

- **`test_classify_genre_ollama`**:
  - **Mocks**: The system's standard terminal commands via `subprocess.run`.
  - **Verifies**: Forces the system to execute the default Ollama fallback. It intercepts the "terminal", feeds it a dummy output (`"House"`), and ensures the python script parses and returns the string properly. It strictly checks that `"ollama"` was the command intended for execution.

- **`test_classify_genre_ollama_fallback_when_gemini_missing_key`**:
  - **Mocks**: Terminal commands via `subprocess.run` & OS environment variables (`os.environ`).
  - **Verifies**: A critical edge-case. When a user configures `USE_GEMINI_API=True` but forgets to set their `GEMINI_API_KEY` in their `.env` file, the script must elegantly failover. This test clears all keys and proves that the script silently switches back to generating an `ollama` terminal query instead of crashing.

- **`test_classify_genre_gemini`**:
  - **Mocks**: The deep internal architecture of Google's network client (`core.classifier.genai.Client`).
  - **Verifies**: Simulates a live remote network response containing a Pydantic-enforced formatted JSON string (`{"genre": "Deep House"}`). The test provides an artificial API key, proves that `google.genai` is instantiated exclusively with that key, verifies the `generate_content()` network call actually occurs, and ensures our script correctly de-serializes the JSON and extracts `"Deep House"`.
