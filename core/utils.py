import os
import fnmatch
from pathlib import Path

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def find_music_files(directory, extensions=None):
    if extensions is None:
        extensions = ['*.mp3', '*.wav', '*.flac', '*.aac', '*.ogg', '*.m4a']
    music_files = []
    for root, _, files in os.walk(directory):
        for ext in extensions:
            for f in fnmatch.filter(files, ext):
                music_files.append(Path(root) / f)
    return music_files

def clean_filename(path, folder_path):
    return path.relative_to(folder_path).with_suffix('').as_posix()
