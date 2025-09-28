@echo off
chcp 65001 >nul
echo ============================================================
echo         MP4 to Text Converter - Korean Optimized
echo         Batch Processing with Local Whisper AI + GPU  
echo ============================================================
echo.

REM Create directories if they don't exist
if not exist "run\input" mkdir "run\input"
if not exist "run\output" mkdir "run\output"

REM Check if MP4 files exist in input directory
if not exist "run\input\*.mp4" (
    echo [ERROR] No MP4 files found in input directory!
    echo.
    echo Please place your MP4 files in:
    echo %CD%\run\input\
    echo.
    echo [INPUT]  Directory: %CD%\run\input\
    echo [OUTPUT] Directory: %CD%\run\output\
    echo.
    pause
    exit /b
)

echo [FOUND] MP4 files for batch processing:
dir "run\input\*.mp4" /b
echo.
echo [INPUT]  Directory: %CD%\run\input\
echo [OUTPUT] Directory: %CD%\run\output\
echo.

echo [BATCH]  All files will use the same processing options
echo [START]  AI transcription batch process...
echo [INFO]   Configure once, process all files automatically
echo [GPU]    Using GPU acceleration for faster processing
echo.

REM Run the Python converter with input directory - it will handle batch processing internally
E:/Study/TY008-PythonUtil/mp4ToText/.venv/Scripts/python.exe mp4_converter_standalone.py

REM Move all output text files to output directory
if exist "*.txt" (
    echo.
    echo [CLEANUP] Moving text files to output directory...
    for %%f in (*.txt) do (
        move "%%f" "run\output\"
        echo [MOVED] %%f
    )
)

echo.
echo ============================================================
echo [COMPLETE] All batch processing completed!
echo [OUTPUT] Check your text files in: %CD%\run\output\
echo ============================================================
pause