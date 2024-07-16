import os
import logging

def remove_duplicates(duplicates):
    for file1, file2 in duplicates:
        try:
            os.remove(file1)
        except Exception as e:
            logging.error(f"Error removing file {file1}: {e}")
