from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
import asyncio
import zipfile
from moviepy.editor import VideoFileClip
from PIL import Image
from config import API_ID, API_HASH, BOT_TOKEN, TEMP_DOWNLOAD_PATH, MAX_FILE_SIZE_MB

app = Client("multi_feature_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

renamed_files = {}  # Stores renamed file info {file_id: new_name}

# Ensure temporary download path exists
os.makedirs(TEMP_DOWNLOAD_PATH, exist_ok=True)


# Helper Functions
def get_file_size_in_mb(size_in_bytes):
    return size_in_bytes / (1024 * 1024)


async def download_file(file_id, file_name):
    """Downloads the file to TEMP_DOWNLOAD_PATH"""
    download_path = os.path.join(TEMP_DOWNLOAD_PATH, file_name)
    return await app.download_media(file_id, file_name=download_path)


def compress_file(file_path, compressed_name):
    """Compresses a file into a ZIP archive"""
    compressed_path = f"{compressed_name}.zip"
    with zipfile.ZipFile(compressed_path, "w") as zipf:
        zipf.write(file_path, arcname=os.path.basename(file_path))
    return compressed_path


def add_watermark_to_image(image_path, watermark_text):
    """Adds watermark text to an image"""
    image = Image.open(image_path)
    watermark = Image.new("RGBA", image.size)
    watermark.paste(image)
    draw = ImageDraw.Draw(watermark)
    draw.text((10, 10), watermark_text, fill=(255, 255, 255, 128))
    watermark.save(image_path)
    return image_path


# Commands
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        f"👋 Hello, {message.from_user.first_name}!\n\n"
        "Welcome to the Multi-Feature File Bot! Here's what I can do:\n"
        "1️⃣ Rename files\n"
        "2️⃣ Compress files\n"
        "3️⃣ Add watermarks\n"
        "4️⃣ Stream files\n"
        "5️⃣ Convert formats\n"
        "6️⃣ More!\n\n"
        "📂 Send me any file to get started!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📢 Visit Our Channel", url="https://t.me/pathan_botz")]]
        ),
    )


@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def file_handler(client, message: Message):
    file = message.document or message.video or message.audio or message.photo
    file_size_mb = get_file_size_in_mb(file.file_size)

    # Check file size limit
    if file_size_mb > MAX_FILE_SIZE_MB:
        await message.reply(f"⚠️ File size exceeds the limit of {MAX_FILE_SIZE_MB} MB.")
        return

    # Save file info for processing
    file_name = file.file_name if hasattr(file, "file_name") else "Unnamed_File"
    file_id = file.file_id
    renamed_files[file_id] = file_name

    # Show options
    await message.reply_text(
        f"📁 **File Received**: `{file_name}`\n"
        f"💾 **Size**: {file_size_mb:.2f} MB\n\n"
        "🔧 What would you like to do?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Rename", callback_data=f"rename|{file_id}")],
                [InlineKeyboardButton("Compress", callback_data=f"compress|{file_id}")],
                [InlineKeyboardButton("Stream", callback_data=f"stream|{file_id}")],
            ]
        ),
    )


@app.on_callback_query(filters.regex("^rename"))
async def rename_callback(client, callback_query):
    file_id = callback_query.data.split("|")[1]

    # Ask for new name
    await callback_query.message.reply_text("Send me the new name for the file:")

    @app.on_message(filters.text)
    async def rename_file(client, rename_message: Message):
        new_name = rename_message.text
        renamed_files[file_id] = new_name
        await callback_query.message.reply_text(f"✅ File renamed to: `{new_name}`.")
        app.remove_handler(rename_file)


@app.on_callback_query(filters.regex("^compress"))
async def compress_callback(client, callback_query):
    file_id = callback_query.data.split("|")[1]
    file_name = renamed_files[file_id]
    downloaded_file = await download_file(file_id, file_name)

    compressed_file = compress_file(downloaded_file, file_name)
    await callback_query.message.reply_document(compressed_file)
    os.remove(compressed_file)  # Clean up after sending


@app.on_callback_query(filters.regex("^stream"))
async def stream_callback(client, callback_query):
    file_id = callback_query.data.split("|")[1]
    file_name = renamed_files.get(file_id, "Unnamed_File")

    # Generate stream link (example Flask server URL)
    stream_url = f"http://127.0.0.1:8000/stream/{file_id}/{file_name}"
    await callback_query.message.reply_text(
        f"🎥 **Stream your file here**: [Stream Now]({stream_url})",
        disable_web_page_preview=True,
    )


if __name__ == "__main__":
    app.run()
  
