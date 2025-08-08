#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads

# Set execute permissions for the script
chmod +x vercel_build.sh
