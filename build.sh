#!/bin/bash

echo "Starting build script..."

# Install required Python packages
pip install -r requirements.txt

# Create nltk_data folder if it doesn't exist
mkdir -p nltk_data

# Download NLTK data (punkt only)
python3 -m nltk.downloader punkt -d ./nltk_data

echo "Build script finished!"
