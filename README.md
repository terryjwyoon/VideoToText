# MP4/M4A to Text Converter

**A complete audio-to-text conversion system with Whisper AI integration and planned Tauri GUI.**

## 🚀 Quick Start

```bash
# Run the master launcher
launcher.bat
```

This provides an interactive menu system for all converter operations.

## 📁 Project Structure

```
mp4ToText/
├── launcher.bat                    # 🎯 ROOT LAUNCHER (START HERE)
├── source/                         # Main source code
│   ├── engine/                     # Python conversion engine
│   │   ├── __init__.py            # Package initialization
│   │   ├── converter.py           # Main conversion logic
│   │   └── cli.py                 # Command line interface
│   ├── gui/                       # 🔮 Tauri GUI (planned)
│   │   └── __init__.py            # Future Tauri implementation
│   └── tests/                     # Test suite
│       ├── __init__.py            # Test package
│       ├── test_converter.py      # Engine tests
│       ├── test_gpu.py            # GPU detection tests
│       └── test_whisper_warnings.py # Whisper AI tests
├── scripts/                       # Build and management scripts
│   ├── launcher.bat               # Main interactive launcher
│   ├── build.bat                  # Build system for executables
│   ├── cleanup.bat                # Project cleanup utilities
│   └── convert_to_text.bat       # Legacy conversion script
├── config/                        # Configuration files
│   ├── mp4_converter.spec         # PyInstaller spec (full version)
│   └── mp4_converter_audio_only.spec # PyInstaller spec (audio-only)
├── run/                           # Runtime directories
│   ├── input/                     # Place your MP4/M4A files here
│   └── output/                    # Converted files appear here
├── release/                       # Built executables
└── docs/                          # Documentation
```

## 🎯 Features

### Current Implementation
- ✅ **MP4 to M4A/MP3 conversion** with progress tracking
- ✅ **M4A to MP3 conversion** for audio format optimization
- ✅ **Audio to Text transcription** using local Whisper AI large-v3
- ✅ **GPU acceleration** support (CUDA)
- ✅ **Batch processing** with single configuration for multiple files
- ✅ **Interactive CLI** with comprehensive menu system
- ✅ **Korean language optimization** with anti-hallucination measures

### Planned Features
- 🔮 **Tauri GUI** - Modern desktop application interface
- 🔮 **Rust backend** - High-performance Tauri integration
- 🔮 **Web frontend** - HTML/CSS/JS user interface

## 🎬 Usage

### 1. Basic Conversion
```bash
# Interactive mode with menu selection
launcher.bat

# Direct Python execution
python source/engine/cli.py
```

### 2. Build Executables
```bash
# From scripts directory
scripts/build.bat full     # Full version (~175MB)
scripts/build.bat audio    # Audio-only (~10MB)  
scripts/build.bat both     # Build both versions
```

### 3. Run Tests
```bash
# GPU detection
python source/tests/test_gpu.py

# Whisper AI functionality
python source/tests/test_whisper_warnings.py

# Converter engine
python source/tests/test_converter.py
```

## 📋 File Types Supported

| Input Format | Output Options | Features |
|-------------|----------------|----------|
| **MP4** | MP3, M4A, Text | Video → Audio/Text conversion |
| **M4A** | MP3, Text | Audio format conversion + transcription |

## 🏗️ Development Structure

### Engine (Python)
- **Location**: `source/engine/`
- **Purpose**: Core conversion functionality
- **Entry Point**: `cli.py` for command line usage
- **Main Module**: `converter.py` with all conversion classes

### GUI (Tauri - Planned)
- **Location**: `source/gui/`
- **Purpose**: Desktop application interface
- **Technology**: Rust backend + HTML/CSS/JS frontend
- **Integration**: Communicates with Python engine

### Tests
- **Location**: `source/tests/`
- **Purpose**: Comprehensive testing suite
- **Coverage**: Engine, GPU, Whisper AI, integration tests

### Scripts
- **Location**: `scripts/`
- **Purpose**: Build, deployment, and utility scripts
- **Main Script**: `launcher.bat` for interactive access

### Configuration
- **Location**: `config/`
- **Purpose**: PyInstaller specs and build configurations

## 🔧 Technical Details

- **Python Engine**: Complete conversion pipeline with Whisper AI
- **GPU Support**: CUDA acceleration when available
- **Batch Processing**: Multiple files with single configuration
- **Progress Tracking**: Real-time conversion progress bars
- **Korean Optimization**: Language-specific transcription settings
- **Anti-hallucination**: Cleanup of common Whisper artifacts

## 🛠️ Development Setup

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/terryjwyoon/VideoToText.git
   cd VideoToText
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Test Installation**:
   ```bash
   launcher.bat
   # Choose option 3 for system tests
   ```

3. **Development**:
   ```bash
   # Work on engine
   python source/engine/cli.py
   
   # Run specific tests
   python source/tests/test_gpu.py
   
   # Build executables
   scripts/build.bat full
   ```

## 🔮 Future Tauri GUI Implementation

The project is structured to support Tauri GUI development:

1. **Rust Backend** (`source/gui/`): Will handle GUI logic and Python engine communication
2. **Web Frontend**: HTML/CSS/JS interface for modern user experience  
3. **Engine Integration**: Seamless communication with existing Python engine
4. **Cross-platform**: Native desktop application for Windows, macOS, Linux

## 💡 Tips

- **Use the launcher**: `launcher.bat` provides the easiest access to all features
- **GPU acceleration**: Ensure CUDA is available for faster transcription
- **Batch processing**: Place multiple files in `run/input/` for bulk conversion
- **Documentation**: All guides accessible through launcher menu
- **Development**: Engine code is modular and ready for GUI integration

## 🔗 Links

- **GitHub Repository**: https://github.com/terryjwyoon/VideoToText
- **Engine Documentation**: See `source/engine/` for implementation details
- **System Tests**: Use launcher Option 3 for diagnostics

---

**Start with `launcher.bat` for the complete experience!** 🚀

**Ready for Tauri GUI development!** 🔮