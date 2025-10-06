# MP4/M4A to Text Converter - Master Control System

## 🚀 Quick Start

**Use the Master Launcher for the best experience:**

```bash
launcher.bat
```

This provides an interactive menu system for all converter operations.

## 📁 Project Structure

```
mp4ToText/
├── launcher.bat                    # 🎯 MASTER LAUNCHER (START HERE)
├── mp4_converter_standalone.py     # Main converter engine
├── build.bat                       # Build system for executables
├── convert_to_text.bat             # Legacy batch file (superseded by launcher)
├── run/
│   ├── input/                      # Place your MP4/M4A files here
│   └── output/                     # Converted files appear here
├── release/                        # Built executables
├── docs/                          # Documentation
└── guides/                        # User guides (*.md files)
```

## 🎯 Master Launcher Features

### 1. File Conversion (Option 1)
- **Auto-detection** of MP4 and M4A files
- **Interactive workflows**:
  - MP4 → Audio (MP3/M4A) 
  - MP4 → Text (Whisper AI)
  - MP4 → Audio + Text
  - M4A → MP3
  - M4A → Text
  - M4A → MP3 + Text
- **Batch processing** with progress tracking
- **GPU acceleration** when available

### 2. Build System (Option 2)
- **Full Version** (~175MB): Complete functionality with Whisper AI
- **Audio-Only Version** (~10MB): Just audio conversion
- **Both Versions**: Build everything at once

### 3. System Tests (Option 3)
- **GPU Detection**: Check CUDA availability
- **Python Environment**: Verify setup
- **Whisper AI Test**: Test speech-to-text
- **Complete Test**: Run all diagnostics

### 4. File Management (Option 4)
- **Clean temporary files**: Remove build artifacts
- **Open project folders**: Quick access to directories
- **File statistics**: View file counts and sizes
- **Clean output directory**: Reset output folder

### 5. Documentation (Option 5)
- **Batch Processing Guide**
- **GPU Optimization Guide** 
- **Text Conversion Guide**
- **Command line help**
- **GitHub repository link**

## 🎬 How to Use

### Basic Usage:
1. Run `launcher.bat`
2. Choose "Convert Files" (Option 1)
3. Place files in `run\input\` when prompted
4. Follow the interactive prompts
5. Find results in `run\output\`

### Advanced Usage:
- Use launcher for system tests and builds
- Access documentation through the launcher
- Manage files through the built-in file manager

## 📋 File Types Supported

| Input Format | Output Options | Features |
|-------------|----------------|----------|
| **MP4** | MP3, M4A, Text | Video → Audio/Text conversion |
| **M4A** | MP3, Text | Audio format conversion + transcription |

## 🔧 Technical Details

- **Engine**: `mp4_converter_standalone.py` (complete solution)
- **Dependencies**: FFmpeg, PyTorch, Whisper AI
- **GPU Support**: CUDA acceleration when available
- **Batch Processing**: Multiple files with single configuration
- **Progress Tracking**: Real-time conversion progress

## 🗂️ Cleanup Completed

The following files were removed/consolidated:
- `source/` directory (old structure) → Now in `mp4_converter_standalone.py`
- Duplicate batch files → Superseded by `launcher.bat`
- Test files are preserved for system diagnostics

## 💡 Tips

- **Use the launcher**: It's the easiest way to access all features
- **GPU acceleration**: Ensure CUDA is available for faster processing
- **Batch processing**: Place multiple files in `run\input\` for bulk conversion
- **Documentation**: All guides accessible through launcher Option 5

## 🔗 Links

- **GitHub Repository**: https://github.com/terryjwyoon/VideoToText
- **Local Documentation**: Available through launcher
- **System Tests**: Run through launcher for diagnostics

---

**Start with `launcher.bat` for the complete experience! 🚀**