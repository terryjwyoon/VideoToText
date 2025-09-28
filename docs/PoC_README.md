# MP4 to Audio Converter - Proof of Concept (PoC)

## Overview

This is a Proof of Concept (PoC) implementation of an MP4 to audio converter that can convert MP4 video files to M4A and MP3 audio formats. The application is designed to be a standalone executable that doesn't require Python installation on the target system.

## Implementation Status

✅ **Completed Features (Order of Implementation #1-3):**

1. **MP4 to M4A Conversion**: Implemented using FFmpeg to extract audio from MP4 files and save as M4A format with AAC codec
2. **M4A to MP3 Conversion**: Implemented conversion from M4A to MP3 format with 128k bitrate
3. **PyInstaller Packaging**: Created standalone executable that can run on Windows systems without Python installation

## Requirements

- **System Requirements**: Windows 11 (tested) or Windows 10
- **External Dependencies**: FFmpeg must be installed and available in system PATH
- **File Formats**: Supports .mp4 and .MP4 file extensions

## Installation & Setup

### Prerequisites
1. **Install FFmpeg**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) and add to system PATH
2. **Verify FFmpeg**: Open command prompt and run `ffmpeg -version` to verify installation

### Getting the PoC
The standalone executable is located in the `release/` directory:
- File: `mp4_converter.exe`
- Size: ~10.5 MB
- No Python installation required

## Usage

### Basic Usage
```bash
# Convert all MP4 files in current directory
mp4_converter.exe

# Convert specific MP4 file
mp4_converter.exe video.mp4

# Show help information
mp4_converter.exe --help
```

### Command Options
- `--help` or `-h`: Show usage information
- `--keep-intermediate`: Keep intermediate M4A files (default: delete them)
- `--m4a-only`: Only convert to M4A format
- `--mp3-only`: Only convert to MP3 format (via M4A intermediate)

### Examples

**Convert all MP4 files in directory to both M4A and MP3:**
```bash
mp4_converter.exe
```

**Convert only to M4A format:**
```bash
mp4_converter.exe --m4a-only
```

**Convert specific file and keep intermediate M4A:**
```bash
mp4_converter.exe video.mp4 --keep-intermediate
```

## How It Works

1. **File Discovery**: Scans current directory for .mp4 and .MP4 files
2. **MP4 → M4A**: Uses FFmpeg to extract audio stream and encode as AAC in M4A container
3. **M4A → MP3**: Converts M4A to MP3 format with 128k bitrate
4. **Cleanup**: Removes intermediate M4A files (unless `--keep-intermediate` is specified)

## Output Format

The converter produces:
- **M4A files**: AAC codec, 128k bitrate
- **MP3 files**: MP3 codec, 128k bitrate
- **File naming**: Original filename with new extension (e.g., `video.mp4` → `video.m4a`, `video.mp3`)

## Example Output

```
============================================================
         MP4 to Audio Converter - PoC
         Converting MP4 files to M4A and MP3
============================================================

Found 2 MP4 file(s) to process:
  1. sample_video.mp4
  2. presentation.mp4

[1/2] Processing: sample_video.mp4
--------------------------------------------------
Successfully converted: sample_video.mp4 -> sample_video.m4a
✓ M4A conversion completed: sample_video.m4a
Successfully converted: sample_video.m4a -> sample_video.mp3
✓ MP3 conversion completed: sample_video.mp3
✓ Cleaned up intermediate file: sample_video.m4a
✓ Successfully processed: sample_video.mp4

[2/2] Processing: presentation.mp4
--------------------------------------------------
Successfully converted: presentation.mp4 -> presentation.m4a
✓ M4A conversion completed: presentation.m4a
Successfully converted: presentation.m4a -> presentation.mp3
✓ MP3 conversion completed: presentation.mp3
✓ Cleaned up intermediate file: presentation.m4a
✓ Successfully processed: presentation.mp4

============================================================
                    CONVERSION SUMMARY
============================================================
Total files processed:     2
Successful conversions:    2
Failed conversions:        0

🎉 All conversions completed successfully!

Press any key to exit...
```

## Troubleshooting

### Common Issues

**"FFmpeg not found" error:**
- Ensure FFmpeg is installed and added to system PATH
- Verify with `ffmpeg -version` in command prompt

**"Input file not found" error:**
- Check file path and ensure MP4 files exist
- Verify file extensions (.mp4 or .MP4)

**"Permission denied" error:**
- Ensure you have write permissions in the directory
- Check if output files are not open in other applications

## Technical Details

### Architecture
- **Language**: Python 3.10
- **Audio Processing**: FFmpeg via ffmpeg-python library
- **Packaging**: PyInstaller for standalone executable
- **Platform**: Windows (tested on Windows 11)

### File Structure
```
mp4ToText/
├── release/
│   └── mp4_converter.exe          # Standalone executable
├── source/
│   └── engine/
│       ├── converter.py           # Core conversion logic
│       ├── main.py               # CLI interface
│       └── __init__.py           # Package initialization
├── mp4_converter_standalone.py    # Combined script for packaging
├── mp4_converter.spec            # PyInstaller specification
├── build.bat                     # Build script
├── test_converter.py            # Test suite
└── requirements.txt             # Python dependencies
```

## Next Steps (Future Implementation)

The following features are planned for future implementation:

4. **Speech Recognition**: Integration with OpenAI Whisper API for MP3 to text conversion
5. **Tauri Backend**: Rust backend to call the Python engine
6. **Tauri Frontend**: HTML/CSS/JS user interface
7. **Full Integration**: Complete desktop application with GUI

## Development

### Building from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_converter.py

# Build executable
.\build.bat
```

### Testing
The PoC has been tested on:
- ✅ Windows 11 (primary target)
- ✅ FFmpeg integration
- ✅ Command-line interface
- ✅ Error handling
- ✅ File processing workflows

---

**Version**: 1.0.0 (PoC)  
**Last Updated**: September 28, 2025  
**Status**: ✅ Implementation Complete (Steps 1-3)