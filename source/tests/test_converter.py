"""
Test script for the MP4 to Audio Converter

This script performs basic tests to ensure the converter functionality works correctly.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the path so we can import the converter
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from source.engine.converter import AudioConverter


def test_converter_initialization():
    """Test that the AudioConverter can be initialized"""
    try:
        converter = AudioConverter()
        print("✓ AudioConverter initialization: PASSED")
        return True
    except Exception as e:
        print(f"✗ AudioConverter initialization: FAILED - {e}")
        return False


def test_ffmpeg_availability():
    """Test that FFmpeg is available on the system"""
    try:
        import ffmpeg
        # Try to get FFmpeg version to test if it's accessible
        ffmpeg.probe('dummy', v='quiet')  # This should fail but not due to FFmpeg missing
        print("✓ FFmpeg availability: PASSED")
        return True
    except ffmpeg.Error:
        # This is expected - we're just testing if FFmpeg is accessible
        print("✓ FFmpeg availability: PASSED")
        return True
    except FileNotFoundError:
        print("✗ FFmpeg availability: FAILED - FFmpeg not found in PATH")
        print("   Please install FFmpeg and add it to your system PATH")
        return False
    except Exception as e:
        print(f"✗ FFmpeg availability: FAILED - {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("         MP4 to Audio Converter - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_converter_initialization,
        test_ffmpeg_availability,
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        if test():
            passed_tests += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The converter is ready to use.")
        return_code = 0
    else:
        print("⚠ Some tests failed. Please address the issues above.")
        return_code = 1
    
    print("=" * 60)
    return return_code


if __name__ == "__main__":
    sys.exit(main())