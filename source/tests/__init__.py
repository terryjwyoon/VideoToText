"""
Test Suite for MP4/M4A to Text Converter

This package contains all test modules for the converter system:
- GPU detection and acceleration tests
- Python environment verification tests  
- Whisper AI functionality tests
- Converter engine unit tests
- Integration tests

Usage:
    python -m source.tests.test_gpu
    python -m source.tests.test_whisper_warnings
    python -m source.tests.test_converter
"""

__version__ = "1.0.0"

# Import all test modules for easy access
try:
    from . import test_gpu, test_whisper_warnings, test_converter
    __all__ = ['test_gpu', 'test_whisper_warnings', 'test_converter']
except ImportError:
    # Tests not yet moved or available
    __all__ = []