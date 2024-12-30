import os
import asyncio
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import API_ID, API_HASH, BOT_TOKEN, TEMP_DOWNLOAD_PATH, MAX_FILE_SIZE_MB, MONGO_URI, DB_NAME

# Initialize bot and MongoDB client
app = Client("multi_feature_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db["users"]
files_collection = db["files"]

# Ensure temporary download path exists
os.makedirs(TEMP_DOWNLOAD_PATH, exist_ok=True)


# Helper Functions
def get_file_size_in_mb(size_in_bytes):
    return size_in_bytes / (1024 * 1024)


def is_premium(user_id):
    """Check if a user is premium."""
    user = users_collection.find_one({"user_id": user_id})
    if user and "premium_expiry" in user:
        expiry_date = user["premium_expiry"]
        return datetime.datetime.now() < expiry_date
    return False


def add_premium_plan(user_id, plan):
    """Add premium plan to user."""
    expiry_date = None
    if plan == "silver":
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=7)
    elif plan == "gold":
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=15)
    elif plan == "platinum":
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=30)

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"premium_plan": plan, "premium_expiry": expiry_date}},
        upsert=True,
    )


async def save_user(user_id, first_name, username):
    """Save user data to MongoDB."""
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
        })


async def save_file_thumbnail(file_id, thumbnail_path):
    """Save the thumbnail for a file."""
    files_collection.update_one(
        {"file_id": file_id},
        {"$set": {"thumbnail": thumbnail_path}},
        upsert=True
    )


# Commands
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    # Save user to MongoDB
    await save_user(user_id, first_name, username)

    await message.reply(
        f"👋 Hello {first_name}, I can help you rename, add watermarks, compress, and stream files.\n\n"
        "You can also manage thumbnails for files.\n\n"
        "Send me a file to get started!"
    )


@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def file_handler(client, message: Message):
    user_id = message.from_user.id
    is_user_premium = is_premium(user_id)

    file = message.document or message.video or message.audio or message.photo
    file_name = file.file_name if hasattr(file, "file_name") else "Unnamed_File"
    file_id = file.file_id
    file_size_mb = get_file_size_in_mb(file.file_size)

    # Check file size limit
    if file_size_mb > MAX_FILE_SIZE_MB:
        await message.reply(f"⚠️ File size exceeds the limit of {MAX_FILE_SIZE_MB} MB.")
        return

    # Store file metadata in the database
    files_collection.update_one(
        {"file_id": file_id},
        {"$set": {"file_name": file_name, "file_size": file_size_mb}},
        upsert=True
    )

    await message.reply_text(
        f"📁 **File Received**: `{file_name}`\n"
        f"💾 **Size**: {file_size_mb:.2f} MB\n\n"
        "🔧 What would you like to do?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Rename", callback_data=f"rename|{file_id}")],
                [InlineKeyboardButton("Add Thumbnail", callback_data=f"add_thumbnail|{file_id}")],
                [InlineKeyboardButton("Remove Thumbnail", callback_data=f"remove_thumbnail|{file_id}")],
                [InlineKeyboardButton("Compress", callback_data=f"compress|{file_id}")],
                [InlineKeyboardButton("Stream", callback_data=f"stream|{file_id}")],
            ]
        ),
    )


@app.on_message(filters.photo)
async def handle_thumbnail(message: Message):
    """Automatically save a shared image as a thumbnail for a file."""
    user_id = message.from_user.id
    file_id = message.reply_to_message.document.file_id if message.reply_to_message and message.reply_to_message.document else None

    if not file_id:
        await message.reply("❌ Please reply to a file to set the thumbnail.")
        return

    # Download the image thumbnail
    thumbnail_path = os.path.join(TEMP_DOWNLOAD_PATH, f"{file_id}_thumbnail.jpg")
    await message.photo.download(thumbnail_path)

    # Save the thumbnail for the file
    await save_file_thumbnail(file_id, thumbnail_path)

    # Notify the user
    await message.reply("✅ Thumbnail has been successfully saved for the file!")


@app.on_callback_query(filters.regex("^remove_thumbnail"))
async def remove_thumbnail(client, callback_query):
    """Handle removing thumbnail from the file."""
    file_id = callback_query.data.split("|")[1]

    # Remove the thumbnail from the file
    await save_file_thumbnail(file_id, "")

    # Delete the thumbnail file if it exists
    file_metadata = files_collection.find_one({"file_id": file_id})
    if "thumbnail" in file_metadata and file_metadata["thumbnail"]:
        thumbnail_path = file_metadata["thumbnail"]
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    await callback_query.message.edit_text("✅ Thumbnail removed from the file.")


# Run the bot
if __name__ == "__main__":
    app.run()
    
