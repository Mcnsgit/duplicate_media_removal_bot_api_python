# import sys
import os
import unittest
from unittest.mock import patch
from duplicate_removal import remove_duplicates
import shutil
from file_handling import generate_file_hash, find_duplicates
class TestDuplicateRemoval(unittest.TestCase):
    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    def test_remove_duplicates(self, mock_exists, mock_remove):
        duplicates = [('file1.mp4', 'file2.mp4')]
        remove_duplicates(duplicates)
        mock_remove.assert_called_with('file1.mp4')

if __name__ == '__main__':
    unittest.main()

    def setUp(self):
        # Create a temporary directory and files for testing
        self.test_dir = 'temp_files'
        os.makedirs(self.test_dir, exist_ok=True)
        self.file1_path = os.path.join(self.test_dir, 'file1.txt')
        self.file2_path = os.path.join(self.test_dir, 'file2.txt')
        self.file3_path = os.path.join(self.test_dir, 'file3.txt')
        with open(self.file1_path, 'w') as f:
            f.write('This is a test file.')
        shutil.copy(self.file1_path, self.file2_path)
        with open(self.file3_path, 'w') as f:
            f.write('This is another test file.')

    def tearDown(self):
        # Remove the temporary directory after testing
        shutil.rmtree(self.test_dir)

    def create_file(self, filename, content):
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    def test_generate_file_hash(self):
        hash1 = generate_file_hash(self.file1_path)
        hash2 = generate_file_hash(self.file2_path)
        hash3 = generate_file_hash(self.file3_path)
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
    
    def test_find_duplicates(self):
        duplicates = find_duplicates(self.test_dir)
        self.assertEqual(len(duplicates), 1)
        self.assertTrue((self.file2_path, self.file1_path) in duplicates or (self.file1_path, self.file2_path) in duplicates)
    
    def test_remove_duplicates(self):
        duplicates = remove_duplicates(self.test_dir)
        self.assertEqual(len(duplicates), 1)
        self.assertFalse(os.path.exists(self.file2_path))
        self.assertTrue(os.path.exists(self.file1_path))
        self.assertTrue(os.path.exists(self.file3_path))

    def test_empty_directory(self):
        # Clean up the test directory
        shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        duplicates = find_duplicates(self.test_dir)
        self.assertEqual(duplicates, [])
        result = remove_duplicates(self.test_dir)
        self.assertEqual(result, [])
    
    def test_no_duplicates(self):
        # Create unique test files
        with open(self.file1_path, 'w') as f:
            f.write('Unique content 1.')
        with open(self.file2_path, 'w') as f:
            f.write('Unique content 2.')
        duplicates = find_duplicates(self.test_dir)
        self.assertEqual(duplicates, [])
        result = remove_duplicates(self.test_dir)
        self.assertEqual(result, [])

    def test_all_duplicates(self):
        # Create identical test files
        with open(self.file1_path, 'w') as f:
            f.write('Duplicate content.')
        shutil.copy(self.file1_path, self.file2_path)
        duplicates = find_duplicates(self.test_dir)
        self.assertEqual(len(duplicates), 1)
        self.assertTrue((self.file2_path, self.file1_path) in duplicates or (self.file1_path, self.file2_path) in duplicates)
        result = remove_duplicates(self.test_dir)
        self.assertEqual(len(result), 1)
        self.assertFalse(os.path.exists(self.file2_path))
        self.assertTrue(os.path.exists(self.file1_path))

    def test_mixed_files(self):
        # Create a mix of duplicate and unique files
        with open(self.file1_path, 'w') as f:
            f.write('Duplicate content.')
        shutil.copy(self.file1_path, self.file2_path)
        with open(self.file3_path, 'w') as f:
            f.write('Unique content.')
        duplicates = find_duplicates(self.test_dir)
        self.assertEqual(len(duplicates), 1)
        self.assertTrue((self.file2_path, self.file1_path) in duplicates or (self.file1_path, self.file2_path) in duplicates)
        result = remove_duplicates(self.test_dir)
        self.assertEqual(len(result), 1)
        self.assertFalse(os.path.exists(self.file2_path))
        self.assertTrue(os.path.exists(self.file1_path))
        self.assertTrue(os.path.exists(self.file3_path))


    def test_files_with_different_extensions(self):
        file1 = self.create_file('file1.txt', 'Same content.')
        file2 = self.create_file('file2.md', 'Same content.')
        duplicates = find_duplicates(self.test_dir)
        self.assertEqual(len(duplicates), 1)
        self.assertTrue((file2, file1) in duplicates or (file1, file2) in duplicates)
        result = remove_duplicates(self.test_dir)
        self.assertEqual(len(result), 1)
        self.assertFalse(os.path.exists(file2) or not os.path.exists(file1))



if __name__ == '__main__':
    unittest.main()