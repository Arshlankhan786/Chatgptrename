# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port the bot is running on
EXPOSE 8080

# Set environment variables (optional, modify according to your needs)
# ENV API_ID='your_api_id'
# ENV API_HASH='your_api_hash'
# ENV BOT_TOKEN='your_bot_token'
# ENV MONGO_URI='mongodb://localhost:27017'
# ENV DB_NAME='file_management_bot_db'
# ENV TEMP_DOWNLOAD_PATH='/path/to/temp/download'

# Run the bot.py script when the container starts
CMD ["python", "bot.py"]
