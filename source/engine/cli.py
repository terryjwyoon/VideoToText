#!/usr/bin/env python3
"""
Command Line Interface for MP4/M4A to Text Converter

This module provides the CLI entry point for the converter engine.
It imports and runs the main function from the converter module.
"""

import sys
import os

# Add the parent directory to path so we can import the engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from source.engine.converter import main

if __name__ == "__main__":
    main()