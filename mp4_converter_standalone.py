"""
MP4 to Audio Converter - Proof of Concept (PoC)
Combined script with converter functionality and CLI interface

This PoC processes MP4 files and converts them to audio formats (M4A and MP3).
Enhanced with progress tracking and interactive format selection.
"""

import os
import sys
import glob
import ffmpeg
import subprocess
import threading
import time
import re
from pathlib import Path


class ProgressTracker:
    """Progress tracking for FFmpeg operations"""
    
    def __init__(self):
        self.duration = 0
        self.current_time = 0
        self.progress_percentage = 0
        self.is_running = False
    
    def get_video_duration(self, input_file: str) -> float:
        """Get duration of video file in seconds using ffprobe"""
        try:
            probe = ffmpeg.probe(input_file)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except:
            # Fallback method using subprocess
            try:
                cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                       '-of', 'csv=p=0', input_file]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return float(result.stdout.strip())
            except:
                return 0
    
    def parse_progress(self, line: str):
        """Parse FFmpeg progress output line"""
        if 'time=' in line:
            time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
            if time_match:
                hours = float(time_match.group(1))
                minutes = float(time_match.group(2))
                seconds = float(time_match.group(3))
                self.current_time = hours * 3600 + minutes * 60 + seconds
                
                if self.duration > 0:
                    self.progress_percentage = min(100, (self.current_time / self.duration) * 100)
    
    def show_progress_bar(self, percentage: float, width: int = 30):
        """Display a progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        print(f'\r[{bar}] {percentage:.1f}%', end='', flush=True)


class AudioConverter:
    """Audio format converter using FFmpeg with progress tracking"""
    
    def __init__(self):
        """Initialize the audio converter"""
        self.supported_input_formats = ['.mp4', '.avi', '.mov', '.mkv']
        self.supported_audio_formats = ['.m4a', '.mp3', '.wav']
        self.progress_tracker = ProgressTracker()
    
    def _run_ffmpeg_with_progress(self, cmd: list, input_file: str, operation_name: str) -> bool:
        """Run FFmpeg command with progress tracking"""
        try:
            # Get duration for progress calculation
            self.progress_tracker.duration = self.progress_tracker.get_video_duration(input_file)
            self.progress_tracker.current_time = 0
            self.progress_tracker.progress_percentage = 0
            self.progress_tracker.is_running = True
            
            print(f"  Converting... ({operation_name})")
            
            # Run FFmpeg with progress output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor progress
            last_percentage = 0
            for line in process.stdout:
                self.progress_tracker.parse_progress(line)
                current_percentage = self.progress_tracker.progress_percentage
                
                # Update progress bar every 1%
                if abs(current_percentage - last_percentage) >= 1:
                    self.progress_tracker.show_progress_bar(current_percentage)
                    last_percentage = current_percentage
            
            process.wait()
            
            # Final progress update
            if process.returncode == 0:
                self.progress_tracker.show_progress_bar(100)
                print()  # New line after progress bar
                return True
            else:
                print(f"\n  Error: FFmpeg process failed with return code {process.returncode}")
                return False
                
        except Exception as e:
            print(f"\n  Error during {operation_name}: {e}")
            return False
        finally:
            self.progress_tracker.is_running = False
    
    def mp4_to_m4a(self, input_file: str, output_file: str = None) -> str:
        """
        Convert MP4 file to M4A format with progress tracking
        
        Args:
            input_file (str): Path to the input MP4 file
            output_file (str, optional): Path to the output M4A file. 
                                       If None, will use input filename with .m4a extension
        
        Returns:
            str: Path to the generated M4A file
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If conversion fails
        """
        input_path = Path(input_file)
        
        # Check if input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = str(input_path.with_suffix('.m4a'))
        
        output_path = Path(output_file)
        
        try:
            # Prepare FFmpeg command with progress - audio only extraction
            cmd = [
                'ffmpeg', '-y', '-i', str(input_path),
                '-vn',  # Disable video stream (audio only)
                '-acodec', 'aac', '-b:a', '128k',
                '-f', 'mp4',  # Force MP4 container format for M4A
                '-progress', 'pipe:1', '-v', 'warning',
                str(output_path)
            ]
            
            success = self._run_ffmpeg_with_progress(cmd, str(input_path), "MP4 → M4A")
            
            # Verify output file was created
            if not success or not output_path.exists():
                raise RuntimeError("Conversion failed: output file was not created")
            
            print(f"  ✓ Successfully converted: {os.path.basename(input_file)} → {os.path.basename(output_file)}")
            return str(output_path)
            
        except Exception as e:
            raise RuntimeError(f"Error during MP4 to M4A conversion: {e}")
    
    def m4a_to_mp3(self, input_file: str, output_file: str = None) -> str:
        """
        Convert M4A file to MP3 format with progress tracking
        
        Args:
            input_file (str): Path to the input M4A file
            output_file (str, optional): Path to the output MP3 file.
                                       If None, will use input filename with .mp3 extension
        
        Returns:
            str: Path to the generated MP3 file
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If conversion fails
        """
        input_path = Path(input_file)
        
        # Check if input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = str(input_path.with_suffix('.mp3'))
        
        output_path = Path(output_file)
        
        try:
            # Prepare FFmpeg command with progress - audio only
            cmd = [
                'ffmpeg', '-y', '-i', str(input_path),
                '-vn',  # Disable video stream (audio only)
                '-acodec', 'mp3', '-b:a', '128k',
                '-progress', 'pipe:1', '-v', 'warning',
                str(output_path)
            ]
            
            success = self._run_ffmpeg_with_progress(cmd, str(input_path), "M4A → MP3")
            
            # Verify output file was created
            if not success or not output_path.exists():
                raise RuntimeError("Conversion failed: output file was not created")
            
            print(f"  ✓ Successfully converted: {os.path.basename(input_file)} → {os.path.basename(output_file)}")
            return str(output_path)
            
        except Exception as e:
            raise RuntimeError(f"Error during M4A to MP3 conversion: {e}")
    
    def convert_mp4_to_mp3(self, input_file: str, output_file: str = None, keep_intermediate: bool = False) -> str:
        """
        Convert MP4 file directly to MP3 format (combines mp4_to_m4a and m4a_to_mp3)
        
        Args:
            input_file (str): Path to the input MP4 file
            output_file (str, optional): Path to the output MP3 file.
                                       If None, will use input filename with .mp3 extension
            keep_intermediate (bool): Whether to keep the intermediate M4A file
        
        Returns:
            str: Path to the generated MP3 file
        """
        input_path = Path(input_file)
        
        # Generate intermediate M4A filename
        m4a_file = str(input_path.with_suffix('.m4a'))
        
        # Generate final MP3 filename if not provided
        if output_file is None:
            output_file = str(input_path.with_suffix('.mp3'))
        
        try:
            # Step 1: Convert MP4 to M4A
            print(f"  Step 1: Converting {os.path.basename(input_file)} to M4A...")
            self.mp4_to_m4a(input_file, m4a_file)
            
            # Step 2: Convert M4A to MP3
            print(f"  Step 2: Converting {os.path.basename(m4a_file)} to MP3...")
            result = self.m4a_to_mp3(m4a_file, output_file)
            
            # Clean up intermediate file if requested
            if not keep_intermediate:
                try:
                    os.remove(m4a_file)
                    print(f"  ✓ Cleaned up intermediate file: {os.path.basename(m4a_file)}")
                except OSError as e:
                    print(f"  ⚠ Warning: Could not remove intermediate file {m4a_file}: {e}")
            
            return result
            
        except Exception as e:
            # Clean up intermediate file on error
            if os.path.exists(m4a_file) and not keep_intermediate:
                try:
                    os.remove(m4a_file)
                except OSError:
                    pass
            raise e
    
    def convert_mp4_to_mp3_direct(self, input_file: str, output_file: str = None) -> str:
        """
        Convert MP4 file directly to MP3 format (single step conversion)
        
        Args:
            input_file (str): Path to the input MP4 file
            output_file (str, optional): Path to the output MP3 file.
                                       If None, will use input filename with .mp3 extension
        
        Returns:
            str: Path to the generated MP3 file
        """
        input_path = Path(input_file)
        
        # Check if input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = str(input_path.with_suffix('.mp3'))
        
        output_path = Path(output_file)
        
        try:
            # Prepare FFmpeg command for direct MP4 to MP3 conversion - audio only
            cmd = [
                'ffmpeg', '-y', '-i', str(input_path),
                '-vn',  # Disable video stream (audio only)
                '-acodec', 'mp3', '-b:a', '128k',
                '-progress', 'pipe:1', '-v', 'warning',
                str(output_path)
            ]
            
            success = self._run_ffmpeg_with_progress(cmd, str(input_path), "MP4 → MP3 (Direct)")
            
            # Verify output file was created
            if not success or not output_path.exists():
                raise RuntimeError("Conversion failed: output file was not created")
            
            print(f"  ✓ Successfully converted: {os.path.basename(input_file)} → {os.path.basename(output_file)}")
            return str(output_path)
            
        except Exception as e:
            raise RuntimeError(f"Error during MP4 to MP3 conversion: {e}")


def find_mp4_files(directory: str = ".") -> list:
    """
    Find all MP4 files in the specified directory
    
    Args:
        directory (str): Directory to search for MP4 files (defaults to current directory)
    
    Returns:
        list: List of MP4 file paths
    """
    patterns = ["*.mp4", "*.MP4"]
    mp4_files = []
    
    for pattern in patterns:
        search_path = os.path.join(directory, pattern)
        mp4_files.extend(glob.glob(search_path))
    
    return sorted(list(set(mp4_files)))  # Remove duplicates and sort


def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("         MP4 to Audio Converter - PoC")
    print("         Converting MP4 files to M4A and MP3")
    print("=" * 60)
    print()


def print_help():
    """Print help information"""
    print("Usage:")
    print("  mp4_converter.exe                    - Interactive mode with format selection")
    print("  mp4_converter.exe <input_file>       - Convert specific MP4 file (interactive)")
    print("  mp4_converter.exe --help             - Show this help message")
    print()
    print("Command Line Options (skip interactive mode):")
    print("  --keep-intermediate    Keep intermediate M4A files (default: delete them)")
    print("  --m4a-only            Only convert to M4A format")
    print("  --mp3-only            Only convert to MP3 format (direct)")
    print("  --both                Convert to both M4A and MP3 formats")
    print()


def select_output_format() -> tuple:
    """
    Interactive format selection menu
    
    Returns:
        tuple: (format_choice, keep_intermediate)
               format_choice: 'm4a', 'mp3', 'both'
               keep_intermediate: bool
    """
    print("🎵 Output Format Selection")
    print("=" * 30)
    print("1. MP3 only (fastest, direct conversion)")
    print("2. M4A only (high quality, smaller size)")
    print("3. Both MP3 and M4A (recommended)")
    print()
    
    while True:
        try:
            choice = input("Select output format (1-3): ").strip()
            if choice == "1":
                format_choice = "mp3"
                break
            elif choice == "2":
                format_choice = "m4a"
                break
            elif choice == "3":
                format_choice = "both"
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)
    
    # Ask about intermediate files only for "both" option
    keep_intermediate = False
    if format_choice == "both":
        print("\n💾 Intermediate File Management")
        print("=" * 35)
        print("When converting to both formats, an intermediate M4A file is created.")
        
        while True:
            try:
                keep_choice = input("Keep intermediate M4A files? (y/n): ").strip().lower()
                if keep_choice in ['y', 'yes']:
                    keep_intermediate = True
                    break
                elif keep_choice in ['n', 'no']:
                    keep_intermediate = False
                    break
                else:
                    print("❌ Please answer 'y' or 'n'.")
                    continue
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                sys.exit(0)
    
    print()
    return format_choice, keep_intermediate


def confirm_conversion(input_files: list, format_choice: str, keep_intermediate: bool) -> bool:
    """
    Show conversion summary and ask for confirmation
    
    Args:
        input_files: List of input MP4 files
        format_choice: Selected output format
        keep_intermediate: Whether to keep intermediate files
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    print("📋 Conversion Summary")
    print("=" * 25)
    print(f"Files to process: {len(input_files)}")
    for i, file in enumerate(input_files, 1):
        print(f"  {i}. {os.path.basename(file)}")
    
    print()
    format_descriptions = {
        'mp3': "MP3 format only (direct conversion)",
        'm4a': "M4A format only",
        'both': f"Both M4A and MP3 formats {'(keeping M4A)' if keep_intermediate else '(removing intermediate M4A)'}"
    }
    print(f"Output format: {format_descriptions[format_choice]}")
    print()
    
    while True:
        try:
            confirm = input("Proceed with conversion? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("❌ Please answer 'y' or 'n'.")
                continue
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def main():
    """Main function for the PoC CLI with enhanced format selection"""
    print_banner()
    
    # Parse command line arguments
    args = sys.argv[1:]
    keep_intermediate_flag = "--keep-intermediate" in args
    m4a_only_flag = "--m4a-only" in args
    mp3_only_flag = "--mp3-only" in args
    both_flag = "--both" in args
    
    # Remove flags from args
    args = [arg for arg in args if not arg.startswith("--")]
    
    # Check for help
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        return
    
    # Initialize converter
    converter = AudioConverter()
    
    # Determine input files
    if args:
        # Specific file provided
        input_files = [args[0]]
        if not os.path.exists(args[0]):
            print(f"❌ Error: File '{args[0]}' not found!")
            sys.exit(1)
    else:
        # Process all MP4 files in current directory
        current_dir = os.getcwd()
        input_files = find_mp4_files(current_dir)
        
        if not input_files:
            print("No MP4 files found in the current directory.")
            print(f"Current directory: {current_dir}")
            print("\nSupported file extensions: .mp4, .MP4")
            print("\n💡 Tip: Place your MP4 files in the same directory as this executable.")
            return
    
    # Determine output format and settings
    if m4a_only_flag or mp3_only_flag or both_flag:
        # Command-line mode (skip interactive selection)
        if m4a_only_flag:
            format_choice = "m4a"
            keep_intermediate = False
        elif mp3_only_flag:
            format_choice = "mp3"
            keep_intermediate = False
        elif both_flag:
            format_choice = "both"
            keep_intermediate = keep_intermediate_flag
        else:
            format_choice = "both"  # Default
            keep_intermediate = keep_intermediate_flag
    else:
        # Interactive mode
        format_choice, keep_intermediate = select_output_format()
        
        # Show confirmation
        if not confirm_conversion(input_files, format_choice, keep_intermediate):
            print("❌ Conversion cancelled by user.")
            return
    
    # Start conversion process
    print("🚀 Starting Conversion Process")
    print("=" * 35)
    print()
    
    # Process each file
    total_files = len(input_files)
    successful_conversions = 0
    failed_conversions = 0
    
    for i, input_file in enumerate(input_files, 1):
        input_path = Path(input_file)
        file_name = input_path.name
        
        print(f"[{i}/{total_files}] Processing: {file_name}")
        print("-" * 50)
        
        try:
            if format_choice == "m4a":
                # Convert only to M4A
                m4a_output = converter.mp4_to_m4a(input_file)
                print(f"✅ M4A conversion completed: {os.path.basename(m4a_output)}")
                
            elif format_choice == "mp3":
                # Convert directly to MP3
                mp3_output = converter.convert_mp4_to_mp3_direct(input_file)
                print(f"✅ MP3 conversion completed: {os.path.basename(mp3_output)}")
                
            elif format_choice == "both":
                # Convert to both M4A and MP3
                m4a_output = converter.mp4_to_m4a(input_file)
                print(f"✅ M4A conversion completed: {os.path.basename(m4a_output)}")
                
                mp3_output = converter.m4a_to_mp3(m4a_output)
                print(f"✅ MP3 conversion completed: {os.path.basename(mp3_output)}")
                
                # Clean up intermediate M4A file if not requested to keep
                if not keep_intermediate:
                    try:
                        os.remove(m4a_output)
                        print(f"🧹 Cleaned up intermediate file: {os.path.basename(m4a_output)}")
                    except OSError as e:
                        print(f"⚠ Warning: Could not remove {m4a_output}: {e}")
            
            successful_conversions += 1
            print(f"🎉 Successfully processed: {file_name}")
            
        except Exception as e:
            failed_conversions += 1
            print(f"❌ Error processing {file_name}: {e}")
        
        print()
    
    # Print summary
    print("=" * 60)
    print("                    🎵 CONVERSION SUMMARY 🎵")
    print("=" * 60)
    print(f"Total files processed:     {total_files}")
    print(f"Successful conversions:    {successful_conversions}")
    print(f"Failed conversions:        {failed_conversions}")
    
    if failed_conversions == 0:
        print("\n🎉 All conversions completed successfully!")
        print("✨ Your audio files are ready to use!")
    else:
        print(f"\n⚠ {failed_conversions} conversion(s) failed. Check the error messages above.")
    
    print("\n📁 Check your files in the current directory.")
    print("\nPress Enter to exit...")
    try:
        input()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)