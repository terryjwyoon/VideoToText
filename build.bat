@echo off
REM Build script for MP4/M4A to Text Converter
REM This script creates standalone executables using PyInstaller
REM Usage: build.bat [full|audio|both]

setlocal enabledelayedexpansion

set BUILD_TYPE=%1
if "%BUILD_TYPE%"=="" set BUILD_TYPE=full

echo ============================================================
echo        Building MP4/M4A to Text Converter - %BUILD_TYPE%
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run this script from the project root directory.
    exit /b 1
)

REM Create release directory if it doesn't exist
if not exist "release" mkdir "release"

if "%BUILD_TYPE%"=="full" goto BUILD_FULL
if "%BUILD_TYPE%"=="audio" goto BUILD_AUDIO
if "%BUILD_TYPE%"=="both" goto BUILD_BOTH

echo Invalid build type: %BUILD_TYPE%
echo Usage: build.bat [full|audio|both]
exit /b 1

:BUILD_FULL
echo Building FULL version (with Whisper AI)...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release\mp4_converter.exe" del "release\mp4_converter.exe"

echo Building executable with PyInstaller...
.venv\Scripts\python.exe -m PyInstaller mp4_converter.spec --noconfirm

if exist "dist\mp4_converter.exe" (
    copy "dist\mp4_converter.exe" "release\"
    for %%f in ("release\mp4_converter.exe") do (
        echo ✅ FULL version built successfully!
        echo    File: release\mp4_converter.exe
        echo    Size: %%~zf bytes (~175MB)
        echo    Features: MP4/M4A conversion + Whisper AI transcription
    )
) else (
    echo ❌ FULL version build failed!
    exit /b 1
)
goto END

:BUILD_AUDIO
echo Building AUDIO-ONLY version...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release\mp4_converter_audio_only.exe" del "release\mp4_converter_audio_only.exe"

echo Building audio-only executable with PyInstaller...
.venv\Scripts\python.exe -m PyInstaller mp4_converter_audio_only.spec --noconfirm

if exist "dist\mp4_converter_audio_only.exe" (
    copy "dist\mp4_converter_audio_only.exe" "release\"
    for %%f in ("release\mp4_converter_audio_only.exe") do (
        echo ✅ AUDIO-ONLY version built successfully!
        echo    File: release\mp4_converter_audio_only.exe
        echo    Size: %%~zf bytes (~10MB)
        echo    Features: MP4/M4A to MP3/M4A conversion only
    )
) else (
    echo ❌ AUDIO-ONLY version build failed!
    exit /b 1
)
goto END

:BUILD_BOTH
echo Building BOTH versions...
echo.
call :BUILD_FULL
echo.
call :BUILD_AUDIO
goto END

:END
echo.
echo ============================================================
echo Build process completed!
echo ============================================================
echo.
echo Available executables in release\ directory:
if exist "release\mp4_converter.exe" echo   ✅ mp4_converter.exe (Full version with AI)
if exist "release\mp4_converter_audio_only.exe" echo   ✅ mp4_converter_audio_only.exe (Audio conversion only)
echo.
echo Usage instructions:
echo   1. Copy executable to desired location
echo   2. Place MP4/M4A files in same directory or run\input\
echo   3. Run the executable for interactive conversion
echo.