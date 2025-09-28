# MP4 to Text Conversion - Usage Instructions

## 🎯 **For Converting MP4 to Text Files**

### **Method 1: Easy Batch File (RECOMMENDED)**

1. **Copy your MP4 files** to the input folder:
   ```
   e:\Study\TY008-PythonUtil\mp4ToText\run\input\
   ```

2. **Double-click**: `convert_to_text.bat`
   - Automatically detects all MP4 files in `run\input\`
   - Converts each MP4 to text using Whisper AI
   - Optimized for Korean language
   - Uses GPU acceleration (RTX4070)
   - Handles large files automatically

3. **Find your text files** in the output folder:
   ```
   e:\Study\TY008-PythonUtil\mp4ToText\run\output\
   ```

### **Method 2: Command Line**

```powershell
# Navigate to the converter directory
cd e:\Study\TY008-PythonUtil\mp4ToText

# Convert specific file from input folder
E:/Study/TY008-PythonUtil/mp4ToText/.venv/Scripts/python.exe mp4_converter_standalone.py "run\input\your_video.mp4"
# Then select "Text Only" option
```

## 📁 **Folder Structure**

```
e:\Study\TY008-PythonUtil\mp4ToText\
├── run\
│   ├── input\          ← Place your MP4 files here
│   └── output\         ← Text files will appear here
├── convert_to_text.bat ← Double-click this to convert
└── ... (other files)
```

## 🔧 **Available Executables**

| File | Purpose | Text Conversion |
|------|---------|----------------|
| `convert_to_text.bat` | **Easy text conversion** | ✅ **Use this one** |
| `mp4_converter_audio_only.exe` | Audio conversion only | ❌ No text features |
| `mp4_converter.exe` | Full features | ⚠️ Has DLL issues |

## ⚡ **Performance Notes**

- **6-hour MP4 file**: Expect 30-60 minutes processing time with GPU
- **Korean audio**: Optimized with Whisper large-v3 model
- **Large files**: Automatically split into chunks for processing
- **GPU acceleration**: Uses your RTX4070 for faster transcription

## 📁 **Output**

Your text files will be saved as:
- `your_video.txt` - Complete transcription
- High accuracy Korean speech recognition
- Includes timestamps and speaker detection when available