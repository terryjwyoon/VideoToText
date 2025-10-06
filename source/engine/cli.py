#!/usr/bin/env python3
"""
Command Line Interface for MP4/M4A to Text Converter

This module provides the CLI entry point for the converter engine.
It imports and runs the main function from the converter module.
"""

import sys
import os

# Add the project root directory to path so we can import the source modules
# This handles being run from various locations including scripts/ subdirectory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up from source/engine/ to project root
sys.path.insert(0, project_root)

from source.engine.converter import main

if __name__ == "__main__":
    main()