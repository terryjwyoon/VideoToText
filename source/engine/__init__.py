"""
MP4/M4A to Text Converter Engine

This package contains the core conversion engine that handles:
- MP4 to M4A conversion
- M4A to MP3 conversion  
- Audio to text transcription using Whisper AI
- Progress tracking and batch processing

The engine is designed to be used by:
- Command line interface (CLI)
- Tauri GUI backend
- Direct Python imports
"""

from .converter import AudioConverter, WhisperTranscriber, AudioSplitter

__version__ = "1.0.0"
__author__ = "Terry Yoon"
__description__ = "Complete MP4/M4A to Text conversion engine with Whisper AI"

__all__ = ['AudioConverter', 'WhisperTranscriber', 'AudioSplitter']