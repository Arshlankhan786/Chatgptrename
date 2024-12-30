import os
import logging
from pyrogram import Client, filters
from pymongo import MongoClient
from config import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    MONGO_URI,
    TEMP_DOWNLOAD_PATH
)

# Ensure the directory exists
os.makedirs(TEMP_DOWNLOAD_PATH, exist_ok=True)

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot"]
users_collection = db["users"]

# Initialize Pyrogram Client
app = Client(
    "RenamerBot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    chat_id = message.chat.id
    user = users_collection.find_one({"_id": chat_id})
    if not user:
        users_collection.insert_one({"_id": chat_id, "premium": False})
    await message.reply("Welcome to the File Renamer Bot! Use /help to see commands.")

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    help_text = (
        "Commands:\n"
        "/start - Start the bot\n"
        "/rename - Rename a file\n"
        "/set_thumbnail - Set a thumbnail\n"
        "/remove_thumbnail - Remove the thumbnail\n"
        "/status - Check bot stats\n"
        "/upgrade - View premium plans\n"
    )
    await message.reply(help_text)

@app.on_message(filters.command("status"))
async def status_handler(client, message):
    total_users = users_collection.count_documents({})
    await message.reply(f"Total users: {total_users}")

# Main handler logic
@app.on_message(filters.document)
async def document_handler(client, message):
    chat_id = message.chat.id
    user = users_collection.find_one({"_id": chat_id})
    
    if not user.get("premium", False):
        if user.get("files_processed", 0) >= 1:
            await message.reply("You can only process one file at a time. Upgrade to premium to process multiple files.")
            return
    
    file = message.document
    file_path = os.path.join(TEMP_DOWNLOAD_PATH, file.file_name)
    await message.reply("Downloading your file...")
    
    downloaded_file = await client.download_media(file, file_path)
    await message.reply(f"File downloaded to {downloaded_file}")

    # Update user's processed file count
    users_collection.update_one({"_id": chat_id}, {"$inc": {"files_processed": 1}})
    
    # Auto-delete after 30 minutes
    async def auto_delete():
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")

    client.loop.call_later(1800, auto_delete)

if __name__ == "__main__":
    logger.info("Starting bot...")
    app.run()
    
    
