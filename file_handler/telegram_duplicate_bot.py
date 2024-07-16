import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram.error import BadRequest
import os
from io import BytesIO
import requests
from file_handling import generate_file_hash

def split_file(file_path, chunk_size=50 * 1024 * 1024):
    file_chunks = []
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunk_file = f"{file_name}.part{chunk_num}.of0"  # Temporarily set 'of' to 0
            with open(chunk_file, 'wb') as chunk_f:
                chunk_f.write(chunk)
            file_chunks.append(chunk_file)
            chunk_num += 1

    # Correct the "of" part in file names
    total_chunks = len(file_chunks)
    corrected_chunks = []
    for chunk_file in file_chunks:
        base_name = os.path.basename(chunk_file)
        new_name = base_name.replace('.of0', f'.of{total_chunks}')
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
class TelegramDuplicateBot:
    def __init__(self, token):
        self.file_hashes = {}
        self.duplicates = {}
        self.chunks = {}
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.configure_logging()
        self.register_handlers()

    def configure_logging(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def register_handlers(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("list_duplicates", self.list_duplicates))
        self.dispatcher.add_handler(MessageHandler(Filters.document, self.handle_document))
        self.dispatcher.add_handler(MessageHandler(Filters.video, self.handle_video))
        self.dispatcher.add_handler(CallbackQueryHandler(self.manage_duplicates, pattern='^duplicate_'))
        self.dispatcher.add_handler(CallbackQueryHandler(self.remove_file, pattern='^remove_'))
    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Hello! Send me videos, and I will find duplicates for you.')

    def download_and_save_chunk(self, file_id, bot):
        try:
            file = bot.get_file(file_id)
            file_path = file.file_path
            file_bytes = BytesIO(requests.get(file_path).content)
            chunk_path = f'/tmp/{file_id}'
            with open(chunk_path, 'wb') as f:
                f.write(file_bytes.getbuffer())
            return chunk_path
        except BadRequest as e:
            if str(e) == "File is too big":
                raise BadRequest("File is too big to process. Please upload a file smaller than 50 MB.")
            else:
                raise

    def handle_document(self, update: Update, context: CallbackContext) -> None:
        bot = context.bot
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name
        if not file_name:
            self.logger.warning(f"Received document with no filename: {file}")
            update.message.reply_text("Received document with no filename.")
            return
        try:
            chunk_path = self.download_and_save_chunk(file_id, bot)
            if file_name not in self.chunks:
                self.chunks[file_name] = []
            if self.is_chunk_file(file_name):
                self.chunks[file_name].append(chunk_path)
                update.message.reply_text(f"Chunk received: {file_name}")
                # Check if all chunks are received and reassemble
                if len(self.chunks[file_name]) == self.expected_chunks(file_name):
                    self.reassemble_and_process(file_name)
            else:
                self.logger.warning(f"Received file that does not match chunk format: {file_name}")
        except BadRequest as e:
            update.message.reply_text(str(e))

    def handle_video(self, update: Update, context: CallbackContext) -> None:
        bot = context.bot
        video = update.message.video
        file_id = video.file_id
        file_name = video.file_name
        if not file_name:
            self.logger.warning(f"Received video with no filename: {video}")
            update.message.reply_text("Received video with no filename.")
            return
        try:
            chunk_path = self.download_and_save_chunk(file_id, bot)
            if file_name not in self.chunks:
                self.chunks[file_name] = []
            if self.is_chunk_file(file_name):
                self.chunks[file_name].append(chunk_path)
                update.message.reply_text(f"Chunk received: {file_name}")
                # Check if all chunks are received and reassemble
                if len(self.chunks[file_name]) == self.expected_chunks(file_name):
                    self.reassemble_and_process(file_name)
            else:
                self.logger.warning(f"Received file that does not match chunk format: {file_name}")
        except BadRequest as e:
            update.message.reply_text(str(e))

    def is_chunk_file(self, file_name):
        if not file_name:
            return False
        parts = file_name.split('.')
        if len(parts) < 3 or not parts[-2].startswith('part') or not parts[-1].startswith('of'):
            return False
        return True

    def expected_chunks(self, file_name):
        try:
            chunk_filenames = [os.path.basename(x) for x in self.chunks[file_name]]
            part_numbers = []
            total_chunks = set()
            for f in chunk_filenames:
                parts = f.split('.')
                if len(parts) < 3 or not parts[-2].startswith('part') or not parts[-1].startswith('of'):
                    self.logger.warning(f"Unexpected chunk filename format: {f}")
                    continue
                part_number = int(parts[-2].replace('part', ''))
                total_chunk_number = int(parts[-1].replace('of', ''))
                part_numbers.append(part_number)
                total_chunks.add(total_chunk_number)
            if len(total_chunks) != 1:
                raise ValueError("Inconsistent chunk metadata.")
            return total_chunks.pop()
        except (IndexError, ValueError) as e:
            self.logger.error(f"Error determining expected chunks for {file_name}: {e}")
            return -1

    def reassemble_and_process(self, file_name):
        if self.expected_chunks(file_name) == -1:
            self.logger.error(f"Cannot reassemble {file_name} due to invalid chunk metadata.")
            return
        chunk_paths = self.chunks[file_name]
        output_file = f'/tmp/{file_name}'
        reassemble_chunks(chunk_paths, output_file)
        file_hash = generate_file_hash(output_file)
        os.remove(output_file)
        if file_hash in self.file_hashes:
            if file_hash not in self.duplicates:
                self.duplicates[file_hash] = []
            self.duplicates[file_hash].append(file_name)
            self.updater.bot.send_message(chat_id=self.updater.bot.id, text=f"Duplicate found: {file_name}")
        else:
            self.file_hashes[file_hash] = file_name
            self.updater.bot.send_message(chat_id=self.updater.bot.id, text=f"File received: {file_name}")
    def list_duplicates(self, update: Update, context: CallbackContext) -> None:
        if not self.duplicates:
            update.message.reply_text("No duplicates found.")
            return

        keyboard = []
        for i, (file_hash, files) in enumerate(self.duplicates.items()):
            keyboard.append([InlineKeyboardButton(f"Duplicate set {i+1}", callback_data=f"duplicate_{file_hash}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Select duplicate set to manage:', reply_markup=reply_markup)

    def manage_duplicates(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()
        file_hash = query.data.split('_')[1]
        files = self.duplicates[file_hash]
        
        keyboard = []
        for file_name in files:
            keyboard.append([InlineKeyboardButton(f"Remove {file_name}", callback_data=f"remove_{file_name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Select files to remove:', reply_markup=reply_markup)

    def remove_file(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()
        file_name = query.data.split('_')[1]
        
        for file_hash, files in self.duplicates.items():
            if file_name in files:
                files.remove(file_name)
                query.edit_message_text(f"File {file_name} removed.")
                if not files:
                    del self.duplicates[file_hash]
                break

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    bot = TelegramDuplicateBot("6539742621:AAFMhaew06ruMxmi8oBKkPtwDuiKxKMBJ8M")
    bot.run()