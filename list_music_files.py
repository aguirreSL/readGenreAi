import os
import fnmatch

# Define the folder path and output file
folder_path = '/Volumes/music/DJSoftware/Archived Songs/'
output_file = './song_list.txt'

# Define common music file extensions
music_extensions = ['*.mp3', '*.wav', '*.flac', '*.aac', '*.ogg', '*.m4a']

# Function to find all music files in the directory
def find_music_files(directory, extensions):
    music_files = []
    for root, dirs, files in os.walk(directory):
        for extension in extensions:
            for filename in fnmatch.filter(files, extension):
                music_files.append(os.path.join(root, filename))
    return music_files

# Find all music files in the specified folder
music_files = find_music_files(folder_path, music_extensions)

# Write the list of music files to the output file, removing the folder_path prefix
with open(output_file, 'w') as file:
    for music_file in music_files:
        # Remove the folder_path prefix from the file path
        relative_path = os.path.relpath(music_file, folder_path)
        file.write(relative_path + '\n')

print(f"Found {len(music_files)} music files. List written to {output_file}")