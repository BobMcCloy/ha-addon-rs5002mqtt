#!/bin/sh
SCRIPT_DIR=$(dirname "$0")
cd $SCRIPT_DIR
echo "Starting ELV RS500 Reader..."
python3 -u reader.py
