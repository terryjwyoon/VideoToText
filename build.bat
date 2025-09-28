@echo off
REM Build script for MP4 to Audio Converter PoC
REM This script creates a standalone executable using PyInstaller

echo ============================================================
echo          Building MP4 to Audio Converter PoC
echo ============================================================
echo.

REM Check if virtual environment is activated
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release\mp4_converter.exe" del "release\mp4_converter.exe"

REM Create release directory if it doesn't exist
if not exist "release" mkdir "release"

echo.
echo Building executable with PyInstaller...
echo.

REM Build the executable
.venv\Scripts\python.exe -m PyInstaller mp4_converter.spec --noconfirm

REM Check if build was successful
if exist "dist\mp4_converter.exe" (
    echo.
    echo ============================================================
    echo Build completed successfully!
    echo ============================================================
    echo.
    
    REM Copy to release directory
    copy "dist\mp4_converter.exe" "release\"
    echo Executable copied to release\mp4_converter.exe
    echo.
    
    REM Show file size
    for %%f in ("release\mp4_converter.exe") do echo File size: %%~zf bytes
    echo.
    echo To test the executable:
    echo   1. Navigate to the release directory
    echo   2. Place some MP4 files in the same folder
    echo   3. Run: mp4_converter.exe
    echo.
    
) else (
    echo.
    echo ============================================================
    echo Build failed!
    echo ============================================================
    echo Please check the error messages above.
    echo.
)

pause