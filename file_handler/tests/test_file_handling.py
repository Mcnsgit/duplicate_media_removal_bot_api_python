import unittest
# import os
from unittest.mock import patch
from file_handling import list_files

class TestFileHandling(unittest.TestCase):
    @patch('os.walk')
    def test_list_files(self, mock_walk):
        mock_walk.return_value = [
            ('.', ('subdir',), ('file_handling.py', 'test_file_handling.py')),
            ('./subdir', (), ('file_in_subdir.py',))
        ]
        files = list_files('.')
        self.assertIn('./file_handling.py', files)
        self.assertIn('./subdir/file_in_subdir.py', files)

if __name__ == '__main__':
    unittest.main()

#     def setUp(self):
#         # Create a temporary directory and files for testing
#         self.test_dir = 'temp_files'
#         os.makedirs(self.test_dir, exist_ok=True)
#         self.file1_path = os.path.join(self.test_dir, 'file1.txt')
#         self.file2_path = os.path.join(self.test_dir, 'file2.txt')
#         self.file3_path = os.path.join(self.test_dir, 'file3.txt')
#         with open(self.file1_path, 'w') as f:
#             f.write('This is a test file.')
#         shutil.copy(self.file1_path, self.file2_path)
#         with open(self.file3_path, 'w') as f:
#             f.write('This is another test file.')

#     def tearDown(self):
#         # Remove the temporary directory and files after testing
#         shutil.rmtree(self.test_dir)

#     def test_list_files(self):
#         files = list_files(self.test_dir)
#         self.assertIn(self.file1_path, files)
#         self.assertIn(self.file2_path, files)
#         self.assertIn(self.file3_path, files)

# if __name__ == '__main__':
#     unittest.main()
