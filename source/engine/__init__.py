"""
MP4 to Text Converter Engine Package

This package contains the core functionality for converting MP4 files to audio formats
and eventually to text using speech recognition.
"""

from .converter import AudioConverter

__version__ = "1.0.0"
__author__ = "MP4 to Text Converter"
__description__ = "Audio format converter using FFmpeg"

__all__ = ['AudioConverter']