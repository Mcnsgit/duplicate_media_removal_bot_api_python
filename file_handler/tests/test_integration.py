import unittest
# import os
from unittest.mock import patch
from file_handling import list_files
from duplicate_removal import remove_duplicates

# Ensure these are defined at the module level to avoid undefined variable errors
file_hashes = {}
duplicates = {}
class TestIntegration(unittest.TestCase):
    @patch('os.walk')
    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    def test_integration(self, mock_exists, mock_remove, mock_walk):
        mock_walk.return_value = [
            ('.', ('subdir',), ('file1.mp4', 'file2.mp4')),
            ('./subdir', (), ('file_in_subdir.mp4',))
        ]
        files = list_files('.')
        duplicates = [(files[0], files[1])]
        remove_duplicates(duplicates)
        mock_remove.assert_called_with('./file1.mp4')

if __name__ == '__main__':
    unittest.main()

#     def setUp(self):
#         # Create a temporary directory for testing
#         self.test_dir = 'temp_files'
#         os.makedirs(self.test_dir, exist_ok=True)
#         self.bot = Bot(token="6539742621:AAFMhaew06ruMxmi8oBKkPtwDuiKxKMBJ8M")
#         self.dispatcher = Dispatcher(self.bot, None, workers=0)
#         self.update = Update(update_id=1234, message=Message(message_id=1234, date=None, chat=None, text=None))

#     def tearDown(self):
#         # Remove the temporary directory after testing
#         shutil.rmtree(self.test_dir)

#     def create_video_file(self, filename, content):
#         file_path = os.path.join(self.test_dir, filename)
#         height, width, layers = content.shape
#         size = (width, height)
#         out = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc(*'mp4v'), 1, size)
#         for _ in range(10):
#             out.write(content)
#         out.release()
#         return file_path

#     def test_list_files(self):
#         # Create test files
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path = self.create_video_file('video1.mp4', frame)
#         files = list_files(self.test_dir)
#         self.assertIn(video_path, files)

#     def test_generate_video_hash(self):
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path = self.create_video_file('video1.mp4', frame)
#         video_hash = generate_video_hash(video_path)
#         self.assertIsNotNone(video_hash)

#     def test_find_duplicates(self):
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path1 = self.create_video_file('video1.mp4', frame)
#         video_path2 = self.create_video_file('video2.mp4', frame)
#         duplicates = find_duplicates(self.test_dir)
#         self.assertEqual(len(duplicates), 1)
#         self.assertIn((video_path2, video_path1), duplicates)

#     def test_handle_document(self):
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path = self.create_video_file('video1.mp4', frame)
#         document = Document(file_id="123", file_name="video1.mp4")
#         message = Message(message_id=1234, date=None, chat=None, text=None, document=document)
#         update = Update(update_id=1234, message=message)
#         context = CallbackContext(self.bot)

#         handle_document(update, context)

#         # Check if file_hashes and duplicates have been updated correctly
#         file_hash = generate_video_hash(video_path)
#         self.assertIn(file_hash, file_hashes)
#         self.assertEqual(file_hashes[file_hash], "123")

#     def test_handle_video(self):
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path = self.create_video_file('video1.mp4', frame)
#         video = Video(file_id="123", file_name="video1.mp4")
#         message = Message(message_id=1234, date=None, chat=None, text=None, video=video)
#         update = Update(update_id=1234, message=message)
#         context = CallbackContext(self.bot)

#         handle_video(update, context)

#         # Check if file_hashes and duplicates have been updated correctly
#         file_hash = generate_video_hash(video_path)
#         self.assertIn(file_hash, file_hashes)
#         self.assertEqual(file_hashes[file_hash], "123")

#     def test_list_duplicates(self):
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path1 = self.create_video_file('video1.mp4', frame)
#         # video_path2 = self.create_video_file('video2.mp4', frame)
#         file_hash = generate_video_hash(video_path1)
#         file_hashes[file_hash] = "123"
#         duplicates[file_hash] = [("video1.mp4", "123"), ("video2.mp4", "124")]

#         update = Update(update_id=1234, message=Message(message_id=1234, date=None, chat=None, text=None))
#         context = CallbackContext(self.bot)

#         list_duplicates(update, context)
#         # Check if bot sent a message with inline keyboard
#         # Here you would mock the bot's send_message method to ensure it was called with expected parameters
#         # Since we can't do it here directly, assume it's checked properly in your test environment

#     def test_manage_duplicates(self):
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path1 = self.create_video_file('video1.mp4', frame)
#         # video_path2 = self.create_video_file('video2.mp4', frame)
#         file_hash = generate_video_hash(video_path1)
#         file_hashes[file_hash] = "123"
#         duplicates[file_hash] = [("video1.mp4", "123"), ("video2.mp4", "124")]

#         callback_query = InlineKeyboardButton(text="Delete video1.mp4", callback_data="delete_123")
#         update = Update(update_id=1234, callback_query=callback_query)
#         context = CallbackContext(self.bot)

#         manage_duplicates(update, context)

#         # Check if bot sent a message with inline keyboard
#         # Here you would mock the bot's edit_message_text method to ensure it was called with expected parameters
#         # Since we can't do it here directly, assume it's checked properly in your test environment

#     def test_delete_file(self):
#         frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#         video_path1 = self.create_video_file('video1.mp4', frame)
#         file_hash = generate_video_hash(video_path1)
#         file_hashes[file_hash] = "123"
#         duplicates[file_hash] = [("video1.mp4", "123")]

#         callback_query = InlineKeyboardButton(text="Delete video1.mp4", callback_data="delete_123")
#         update = Update(update_id=1234, callback_query=callback_query)
#         context = CallbackContext(self.bot)
        
        
#         delete_file(update, context)


# if __name__ == '__main__':
#     unittest.main()
