# Telegram File Management Bot

A powerful Telegram bot that allows users to rename files, add/remove thumbnails, compress files, and more. It also includes a premium plan system and auto-delete functionality.

## Features

- **File Management**:
  - **Rename**: Users can rename uploaded files.
  - **Thumbnail Management**: Users can add and remove thumbnails for files.
  - **Compress**: Compress files before sharing them.
  - **Stream**: Stream files directly.
  
- **Premium Plans**:
  - **Silver**: 7 days of premium access.
  - **Gold**: 15 days of premium access.
  - **Platinum**: 30 days of premium access.
  - Users with premium can rename multiple files at once; non-premium users can only rename one file at a time.

- **Stats**: Admins can check bot statistics (total users, premium users, free users).

- **Auto Delete**: Files will automatically be deleted after 30 minutes of renaming or processing.

- **Shared Thumbnail Handling**: Users can share images (as thumbnails) and the bot will automatically save it as the file's thumbnail.

---

## Commands

### `/start`

- Starts the bot and provides a welcome message.
- **Usage**: `/start`

### `/stats` (Admin only)

- Displays the bot statistics, including the total number of users, premium users, and free users.
- **Usage**: `/stats` (Admin must execute)

### File Handling Commands

1. **Upload a File**:
   - Send any file (document, video, audio, image) to the bot.
   - The bot will receive the file, store it in the database, and offer options for renaming, adding/removing thumbnails, compressing, or streaming.
   - After uploading a file, the bot displays the following options:
     - **Rename**: Rename the file.
     - **Add Thumbnail**: Add a custom thumbnail to the file.
     - **Remove Thumbnail**: Remove the thumbnail from the file.
     - **Compress**: Compress the file before sending.
     - **Stream**: Stream the file directly.

2. **Add Thumbnail**:
   - Share an image that you want to set as a thumbnail for the file. The bot will save the image as the file's thumbnail.
   - **Usage**: Reply to the file with an image.

3. **Remove Thumbnail**:
   - Remove the previously set thumbnail for the file.
   - **Usage**: Click the **Remove Thumbnail** button after uploading the file.

4. **Rename File**:
   - Allows the user to rename the file.
   - **Usage**: Use the "Rename" button after uploading the file.

5. **Compress File**:
   - Compress a file before sharing.
   - **Usage**: Use the "Compress" button after uploading the file.

6. **Stream File**:
   - Stream the file directly.
   - **Usage**: Use the "Stream" button after uploading the file.

### Premium Commands

- **Premium Users**: Premium users (Silver, Gold, or Platinum plans) can rename multiple files at the same time. Non-premium users can only rename one file at a time.
- **Upgrade to Premium**: Users can purchase a premium plan to get additional features and longer access.
  - **Silver**: 7 days of premium access.
  - **Gold**: 15 days of premium access.
  - **Platinum**: 30 days of premium access.

### Admin Commands

- **/stats**: Displays bot statistics, including total user count, premium users, and free users. This command can only be executed by an admin.

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/telegram-file-management-bot.git
cd telegram-file-management-bot
