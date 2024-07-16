import os
import hashlib
from moviepy.editor import VideoFileClip
import logging

def generate_video_hash(file_path):
    hasher = hashlib.sha256()
    try:
        video = VideoFileClip(file_path)
        for frame in video.iter_frames(fps=1):
            hasher.update(frame.tobytes())
    except Exception as e:
        logging.error(f"Error reading video file {file_path}: {e}")
        return None
    return hasher.hexdigest()

def find_duplicates(directory):
    hashes = {}
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            file_hash = generate_video_hash(file_path)
            if file_hash in hashes:
                print(f"Duplicate found: {file_path} and {hashes[file_hash]}")
            else:
                hashes[file_hash] = file_path

directory = "/path/to/directory"
find_duplicates(directory)
