import os
import logging
import hashlib

def list_files(directory):
    files = []
    try:
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
    except Exception as e:
        logging.error(f"Error listing files in directory {directory}: {e}")
    return files

def generate_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def find_duplicates(directory):
    hashes = {}
    duplicates = []
    files = list_files(directory)
    for file_path in files:
        file_hash = generate_file_hash(file_path)
        if file_hash in hashes:
            duplicates.append((file_path, hashes[file_hash]))
        else:
            hashes[file_hash] = file_path
    return duplicates

def split_file(file_path, chunk_size=50 * 1024 * 1024):
    file_chunks = []
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunk_file = f"{file_name}.part{chunk_num}.of{chunk_num+1}"  # Temporarily set of to chunk_num+1
            with open(chunk_file, 'wb') as chunk_f:
                chunk_f.write(chunk)
            file_chunks.append(chunk_file)
            chunk_num += 1

    # Correct the "of" part in file names
    total_chunks = len(file_chunks)
    corrected_chunks = []
    for chunk_file in file_chunks:
        base_name = os.path.basename(chunk_file)
        new_name = base_name.replace(f".of{chunk_num}", f".of{total_chunks}")
        new_path = os.path.join(os.path.dirname(chunk_file), new_name)
        os.rename(chunk_file, new_path)
        corrected_chunks.append(new_path)

    return corrected_chunks


def reassemble_chunks(chunk_files, output_file):
    with open(output_file, 'wb') as f:
        for chunk_file in chunk_files:
            with open(chunk_file, 'rb') as chunk_f:
                f.write(chunk_f.read())
            os.remove(chunk_file)
