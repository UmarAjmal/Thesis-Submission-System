#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to check if a command exists
command_exists () {
    command -v "$1" >/dev/null 2>&1 ;
}

# Check for Python installation
if ! command_exists python3 ; then
    echo "Python3 is not installed. Please install Python3 to proceed."
    exit 1
fi

# Check for pip installation
if ! command_exists pip3 ; then
    echo "pip3 is not installed. Installing pip3..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Create a virtual environment named 'venv' if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment 'venv' already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip to the latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."

# Core Flask Framework
echo "Installing Flask>=2.3.2..."
pip install "Flask>=2.3.2"

# User Session Management
echo "Installing Flask-Login>=0.6.2..."
pip install "Flask-Login>=0.6.2"

# Form Handling and Validation
echo "Installing Flask-WTF>=1.1.1..."
pip install "Flask-WTF>=1.1.1"

# Database ORM
echo "Installing Flask-SQLAlchemy>=3.0.5..."
pip install "Flask-SQLAlchemy>=3.0.5"

# Migrations Management
echo "Installing Flask-Migrate>=4.0.4..."
pip install "Flask-Migrate>=4.0.4"

# Password Hashing
echo "Installing bcrypt>=4.0.1..."
pip install "bcrypt>=4.0.1"

# Security and Utilities
echo "Installing Werkzeug>=2.3.3..."
pip install "Werkzeug>=2.3.3"

# Environment Variable Management
echo "Installing python-dotenv>=0.21.0..."
pip install "python-dotenv>=0.21.0"

# Email Handling
echo "Installing Flask-Mail>=0.9.1..."
pip install "Flask-Mail>=0.9.1"

# Caching Mechanism
echo "Installing Flask-Caching>=1.11.1..."
pip install "Flask-Caching>=1.11.1"

# Cross-Origin Resource Sharing (Optional)
echo "Installing Flask-CORS>=3.0.10..."
pip install "Flask-CORS>=3.0.10"

# API Development (Optional)
echo "Installing Flask-RESTful>=0.3.9..."
pip install "Flask-RESTful>=0.3.9"

# Testing Frameworks (Optional)
echo "Installing pytest>=7.3.1..."
pip install "pytest>=7.3.1"

echo "Installing Flask-Testing>=0.8.1..."
pip install "Flask-Testing>=0.8.1"

# Additional Dependencies (Optional)
echo "Installing Flask-Bootstrap>=3.3.7.1..."
pip install "Flask-Bootstrap>=3.3.7.1"

echo "All dependencies installed successfully!"

# Deactivate virtual environment after installation
echo "Deactivating virtual environment..."
deactivate
