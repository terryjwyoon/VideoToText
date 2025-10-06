@echo off
REM Cleanup script for MP4/M4A to Text Converter project
REM This script removes unnecessary files and directories

echo ============================================================
echo          Project Cleanup - Remove Unnecessary Files
echo ============================================================
echo.

echo Files and directories to be removed:
echo.

REM Check what will be removed (from project root)
if exist "..\__pycache__\" (
    echo [FOLDER] __pycache__\ - Python cache files
    set CLEANUP_NEEDED=1
)

if exist "..\build\" (
    echo [FOLDER] build\ - PyInstaller build artifacts
    set CLEANUP_NEEDED=1
)

if exist "..\dist\" (
    echo [FOLDER] dist\ - PyInstaller distribution files
    set CLEANUP_NEEDED=1
)

if exist "..\..\*.pyc" (
    echo [FILES]  *.pyc - Compiled Python files
    set CLEANUP_NEEDED=1
)

if exist "..\mp4_converter_standalone.py" (
    echo [FILE]   mp4_converter_standalone.py - Old standalone file (now in source/engine/)
    set CLEANUP_NEEDED=1
)

if not defined CLEANUP_NEEDED (
    echo No cleanup needed. Project is already clean!
    pause
    exit /b 0
)

echo.
echo These files are safe to remove as they are either:
echo   - Superseded by the new modular structure
echo   - Temporary build artifacts that can be regenerated
echo   - Python cache files
echo.

set /p confirm="Proceed with cleanup? (y/N): "
if /i not "%confirm%"=="y" (
    echo Cleanup cancelled.
    pause
    exit /b 0
)

echo.
echo Performing cleanup...

REM Remove directories (from project root)
if exist "..\__pycache__\" (
    rmdir /s /q "..\__pycache__"
    echo ✅ Removed: __pycache__\
)

if exist "..\build\" (
    rmdir /s /q "..\build"
    echo ✅ Removed: build\
)

if exist "..\dist\" (
    rmdir /s /q "..\dist"
    echo ✅ Removed: dist\
)

REM Remove old standalone file if it exists
if exist "..\mp4_converter_standalone.py" (
    del "..\mp4_converter_standalone.py"
    echo ✅ Removed: mp4_converter_standalone.py (superseded by source/engine/)
)

REM Remove compiled Python files
if exist "..\..\*.pyc" (
    del /q "..\..\*.pyc"
    echo ✅ Removed: *.pyc files
)

echo.
echo ============================================================
echo Cleanup completed successfully!
echo ============================================================
echo.
echo Project structure is now optimized:
echo   ✅ Modular structure in source/ directory
echo   ✅ Engine ready for Tauri GUI integration
echo   ✅ Tests organized in source/tests/
echo   ✅ Scripts organized in scripts/
echo   ✅ No unnecessary files remaining
echo.
echo Next steps:
echo   1. Run '../launcher.bat' for interactive access
echo   2. Test the system with your files
echo   3. Begin Tauri GUI development in source/gui/
echo.

pause