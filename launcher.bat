@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM          MP4/M4A to Text Converter - Master Launcher
REM     Complete Management System for Audio/Text Processing
REM ============================================================

:MAIN_MENU
cls
echo ============================================================
echo         MP4/M4A to Text Converter - Master Control
echo         Enhanced PoC with Local Whisper AI + GPU Support
echo ============================================================
echo.
echo Select an option:
echo.
echo [1] 🎬 Convert Files (Interactive Mode)
echo     - Auto-detect MP4/M4A files and choose workflows
echo.
echo [2] 🔧 Build Executables (PyInstaller)
echo     - Create standalone .exe files for distribution
echo.
echo [3] 🧪 System Tests
echo     - Test GPU, Python environment, and dependencies
echo.
echo [4] 📁 File Management
echo     - Clean temporary files and organize outputs
echo.
echo [5] 📖 Documentation
echo     - View guides and help information
echo.
echo [0] ❌ Exit
echo.
set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto CONVERT_FILES
if "%choice%"=="2" goto BUILD_EXECUTABLES
if "%choice%"=="3" goto SYSTEM_TESTS
if "%choice%"=="4" goto FILE_MANAGEMENT
if "%choice%"=="5" goto DOCUMENTATION
if "%choice%"=="0" goto EXIT
echo Invalid choice. Please try again.
pause
goto MAIN_MENU

:CONVERT_FILES
cls
echo ============================================================
echo                    File Conversion Mode
echo ============================================================
echo.

REM Create directories if they don't exist
if not exist "run\input" mkdir "run\input"
if not exist "run\output" mkdir "run\output"

REM Check for MP4 files
set mp4_count=0
for %%f in ("run\input\*.mp4") do set /a mp4_count+=1

REM Check for M4A files  
set m4a_count=0
for %%f in ("run\input\*.m4a") do set /a m4a_count+=1

if %mp4_count%==0 if %m4a_count%==0 (
    echo [INFO] No MP4 or M4A files found in input directory!
    echo.
    echo Please place your files in:
    echo %CD%\run\input\
    echo.
    echo Supported formats: .mp4, .MP4, .m4a, .M4A
    echo.
    echo [1] Open input folder
    echo [2] Return to main menu
    echo.
    set /p subchoice="Choose option (1-2): "
    if "!subchoice!"=="1" start explorer "%CD%\run\input"
    pause
    goto MAIN_MENU
)

echo Found files:
if %mp4_count% gtr 0 echo   - %mp4_count% MP4 file(s)
if %m4a_count% gtr 0 echo   - %m4a_count% M4A file(s)
echo.
echo [INPUT]  Directory: %CD%\run\input\
echo [OUTPUT] Directory: %CD%\run\output\
echo.

REM Run the converter
echo Starting interactive converter...
echo.
.venv\Scripts\python.exe mp4_converter_standalone.py

echo.
echo Processing completed! Check the output directory for results.
echo.
echo [1] Open output folder
echo [2] Return to main menu
echo [3] Exit
echo.
set /p subchoice="Choose option (1-3): "
if "!subchoice!"=="1" start explorer "%CD%\run\output"
if "!subchoice!"=="3" goto EXIT
goto MAIN_MENU

:BUILD_EXECUTABLES
cls
echo ============================================================
echo                   Build Executables Mode
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please ensure you're running from the project root directory.
    pause
    goto MAIN_MENU
)

echo Select build type:
echo.
echo [1] 📦 Full Version (with Whisper AI) - ~175MB
echo     - Complete audio-to-text conversion
echo     - GPU acceleration support
echo.
echo [2] 🎵 Audio-Only Version - ~10MB
echo     - MP4/M4A to MP3/M4A conversion only
echo     - No AI transcription
echo.
echo [3] 🔄 Both Versions
echo.
echo [0] Return to main menu
echo.
set /p buildchoice="Choose build type (0-3): "

if "%buildchoice%"=="1" goto BUILD_FULL
if "%buildchoice%"=="2" goto BUILD_AUDIO
if "%buildchoice%"=="3" goto BUILD_BOTH
if "%buildchoice%"=="0" goto MAIN_MENU
echo Invalid choice. Please try again.
pause
goto BUILD_EXECUTABLES

:BUILD_FULL
echo.
echo Building full version with Whisper AI...
call build.bat full
pause
goto MAIN_MENU

:BUILD_AUDIO
echo.
echo Building audio-only version...
call build.bat audio
pause
goto MAIN_MENU

:BUILD_BOTH
echo.
echo Building both versions...
call build.bat full
call build.bat audio
pause
goto MAIN_MENU

:SYSTEM_TESTS
cls
echo ============================================================
echo                     System Tests Mode
echo ============================================================
echo.

echo Select test type:
echo.
echo [1] 🔍 GPU Detection Test
echo     - Check CUDA availability and GPU acceleration
echo.
echo [2] 🐍 Python Environment Test
echo     - Verify Python setup and dependencies
echo.
echo [3] 🎤 Whisper AI Test
echo     - Test speech-to-text functionality
echo.
echo [4] 🔄 Complete System Test
echo     - Run all tests sequentially
echo.
echo [0] Return to main menu
echo.
set /p testchoice="Choose test type (0-4): "

if "%testchoice%"=="1" goto TEST_GPU
if "%testchoice%"=="2" goto TEST_PYTHON
if "%testchoice%"=="3" goto TEST_WHISPER
if "%testchoice%"=="4" goto TEST_ALL
if "%testchoice%"=="0" goto MAIN_MENU
echo Invalid choice. Please try again.
pause
goto SYSTEM_TESTS

:TEST_GPU
echo.
echo Running GPU detection test...
.venv\Scripts\python.exe test_gpu.py
pause
goto MAIN_MENU

:TEST_PYTHON
echo.
echo Testing Python environment...
.venv\Scripts\python.exe -c "import sys; print(f'Python version: {sys.version}'); import mp4_converter_standalone; print('✅ Main converter loaded successfully')"
pause
goto MAIN_MENU

:TEST_WHISPER
echo.
echo Testing Whisper AI functionality...
.venv\Scripts\python.exe test_whisper_warnings.py
pause
goto MAIN_MENU

:TEST_ALL
echo.
echo Running complete system test...
echo.
echo === GPU Test ===
.venv\Scripts\python.exe test_gpu.py
echo.
echo === Python Environment Test ===
.venv\Scripts\python.exe -c "import sys; print(f'Python version: {sys.version}'); import mp4_converter_standalone; print('✅ Main converter loaded successfully')"
echo.
echo === Whisper Test ===
.venv\Scripts\python.exe test_whisper_warnings.py
echo.
echo === Converter Syntax Test ===
.venv\Scripts\python.exe -c "import mp4_converter_standalone; print('✅ All tests completed successfully')"
pause
goto MAIN_MENU

:FILE_MANAGEMENT
cls
echo ============================================================
echo                  File Management Mode
echo ============================================================
echo.

echo Select management option:
echo.
echo [1] 🧹 Clean Temporary Files
echo     - Remove __pycache__, build artifacts
echo.
echo [2] 📁 Open Project Folders
echo     - Quick access to input/output directories
echo.
echo [3] 📊 Show File Statistics
echo     - Display file counts and sizes
echo.
echo [4] 🗑️ Clean Output Directory
echo     - Remove all generated files (with confirmation)
echo.
echo [0] Return to main menu
echo.
set /p mgmtchoice="Choose option (0-4): "

if "%mgmtchoice%"=="1" goto CLEAN_TEMP
if "%mgmtchoice%"=="2" goto OPEN_FOLDERS
if "%mgmtchoice%"=="3" goto SHOW_STATS
if "%mgmtchoice%"=="4" goto CLEAN_OUTPUT
if "%mgmtchoice%"=="0" goto MAIN_MENU
echo Invalid choice. Please try again.
pause
goto FILE_MANAGEMENT

:CLEAN_TEMP
echo.
echo Cleaning temporary files...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.pyc" del /q "*.pyc"
echo ✅ Temporary files cleaned.
pause
goto MAIN_MENU

:OPEN_FOLDERS
echo.
echo Opening project folders...
start explorer "%CD%\run\input"
start explorer "%CD%\run\output"
start explorer "%CD%\release"
echo ✅ Folders opened in Windows Explorer.
pause
goto MAIN_MENU

:SHOW_STATS
echo.
echo === Project File Statistics ===
echo.
if exist "run\input" (
    echo INPUT DIRECTORY:
    for %%f in ("run\input\*.mp4") do echo   MP4: %%~nxf [%%~zf bytes]
    for %%f in ("run\input\*.m4a") do echo   M4A: %%~nxf [%%~zf bytes]
)
echo.
if exist "run\output" (
    echo OUTPUT DIRECTORY:
    for %%f in ("run\output\*.mp3") do echo   MP3: %%~nxf [%%~zf bytes]
    for %%f in ("run\output\*.m4a") do echo   M4A: %%~nxf [%%~zf bytes]
    for %%f in ("run\output\*.txt") do echo   TXT: %%~nxf [%%~zf bytes]
)
echo.
if exist "release" (
    echo EXECUTABLES:
    for %%f in ("release\*.exe") do echo   EXE: %%~nxf [%%~zf bytes]
)
pause
goto MAIN_MENU

:CLEAN_OUTPUT
echo.
echo ⚠️  WARNING: This will delete all files in the output directory!
echo.
if exist "run\output" (
    dir "run\output" /B
    echo.
)
set /p confirm="Are you sure you want to delete all output files? (y/N): "
if /i "!confirm!"=="y" (
    if exist "run\output" (
        del /q "run\output\*.*" 2>nul
        echo ✅ Output directory cleaned.
    )
) else (
    echo ❌ Operation cancelled.
)
pause
goto MAIN_MENU

:DOCUMENTATION
cls
echo ============================================================
echo                   Documentation Mode
echo ============================================================
echo.

echo Available documentation:
echo.
echo [1] 📖 Batch Processing Guide
echo [2] 🚀 GPU Optimization Guide  
echo [3] 🔧 Missing Audio Fix Guide
echo [4] 📝 Text Conversion Guide
echo [5] 💡 Show Help (Command Line Options)
echo [6] 🌐 Open GitHub Repository
echo.
echo [0] Return to main menu
echo.
set /p docchoice="Choose documentation (0-6): "

if "%docchoice%"=="1" if exist "BATCH_PROCESSING_GUIDE.md" type "BATCH_PROCESSING_GUIDE.md" & pause & goto MAIN_MENU
if "%docchoice%"=="2" if exist "GPU_OPTIMIZATION_GUIDE.md" type "GPU_OPTIMIZATION_GUIDE.md" & pause & goto MAIN_MENU
if "%docchoice%"=="3" if exist "MISSING_AUDIO_FIX.md" type "MISSING_AUDIO_FIX.md" & pause & goto MAIN_MENU
if "%docchoice%"=="4" if exist "TEXT_CONVERSION_GUIDE.md" type "TEXT_CONVERSION_GUIDE.md" & pause & goto MAIN_MENU
if "%docchoice%"=="5" .venv\Scripts\python.exe mp4_converter_standalone.py --help & pause & goto MAIN_MENU
if "%docchoice%"=="6" start https://github.com/terryjwyoon/VideoToText & goto MAIN_MENU
if "%docchoice%"=="0" goto MAIN_MENU

echo File not found or invalid choice.
pause
goto MAIN_MENU

:EXIT
echo.
echo Thank you for using MP4/M4A to Text Converter!
echo Visit: https://github.com/terryjwyoon/VideoToText
pause
exit /b 0