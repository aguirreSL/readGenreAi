from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE

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
    """Write predicted genre to file metadata"""
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
