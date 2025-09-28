@echo off
chcp 65001 >nul
echo ============================================================
echo         MP4 to Text Converter - Korean Optimized
echo         Using Local Whisper AI with GPU Acceleration  
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

echo [FOUND] MP4 files for conversion:
dir "run\input\*.mp4" /b
echo.
echo [INPUT]  Directory: %CD%\run\input\
echo [OUTPUT] Directory: %CD%\run\output\
echo.

echo [START] AI transcription process...
echo [INFO]  This may take a while for large files (6+ hours)
echo [GPU]   Using GPU acceleration for faster processing
echo.

REM Process each MP4 file in the input directory
for %%f in ("run\input\*.mp4") do (
    echo.
    echo [PROCESSING] %%~nxf
    echo ----------------------------------------
    
    REM Run the Python converter with specific input file
    E:/Study/TY008-PythonUtil/mp4ToText/.venv/Scripts/python.exe mp4_converter_standalone.py "%%f"
    
    REM Move the output text file to output directory if it exists
    if exist "%%~nf.txt" (
        move "%%~nf.txt" "run\output\"
        echo [SUCCESS] Text file moved to output directory: %%~nf.txt
    )
)

echo.
echo ============================================================
echo [COMPLETE] All conversions completed!
echo [OUTPUT] Check your text files in: %CD%\run\output\
echo ============================================================
pause