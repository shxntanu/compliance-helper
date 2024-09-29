#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "/workspaces/${workspaceFolderBasename}/.venv" ]; then
    python -m venv /workspaces/${workspaceFolderBasename}/.venv
fi

# Activate virtual environment
source /workspaces/${workspaceFolderBasename}/.venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r /workspaces/${workspaceFolderBasename}/requirements.txt

# Deactivate virtual environment
deactivate

echo "Virtual environment setup complete."