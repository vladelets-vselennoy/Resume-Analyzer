#!/bin/bash

# Create virtual environment
python -m venv resumeenv
source resumeenv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the analyzer
python src/main2.py