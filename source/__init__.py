"""
Source Package for MP4/M4A to Text Converter

This is the main source package containing:
- engine/: Core conversion functionality
- gui/: Tauri GUI implementation (planned)
- tests/: Test suite for all components

Project Structure:
    source/
    ├── engine/     # Python conversion engine
    ├── gui/        # Tauri GUI (Rust + HTML/CSS/JS)
    └── tests/      # Test suite
"""

__version__ = "1.0.0"
__description__ = "MP4/M4A to Text Converter with Whisper AI and Tauri GUI"

# Import main components
from . import engine
from . import tests

# GUI will be imported when Tauri implementation is added
try:
    from . import gui
    __all__ = ['engine', 'gui', 'tests']
except ImportError:
    __all__ = ['engine', 'tests']