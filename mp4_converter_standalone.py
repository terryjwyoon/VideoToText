"""
MP4 to Audio Converter - Proof of Concept (PoC)
Combined script with converter functionality and CLI interface

This PoC processes MP4 files and converts them to audio formats (M4A and MP3).
"""

import os
import sys
import glob
import ffmpeg
from pathlib import Path


class AudioConverter:
    """Audio format converter using FFmpeg"""
    
    def __init__(self):
        """Initialize the audio converter"""
        self.supported_input_formats = ['.mp4', '.avi', '.mov', '.mkv']
        self.supported_audio_formats = ['.m4a', '.mp3', '.wav']
    
    def mp4_to_m4a(self, input_file: str, output_file: str = None) -> str:
        """
        Convert MP4 file to M4A format
        
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
            # Use FFmpeg to extract audio and convert to M4A
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(stream, str(output_path), acodec='aac', audio_bitrate='128k')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Verify output file was created
            if not output_path.exists():
                raise RuntimeError("Conversion failed: output file was not created")
            
            print(f"Successfully converted: {input_file} -> {output_file}")
            return str(output_path)
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during MP4 to M4A conversion: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during MP4 to M4A conversion: {e}")
    
    def m4a_to_mp3(self, input_file: str, output_file: str = None) -> str:
        """
        Convert M4A file to MP3 format
        
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
            # Use FFmpeg to convert M4A to MP3
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(stream, str(output_path), acodec='mp3', audio_bitrate='128k')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Verify output file was created
            if not output_path.exists():
                raise RuntimeError("Conversion failed: output file was not created")
            
            print(f"Successfully converted: {input_file} -> {output_file}")
            return str(output_path)
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during M4A to MP3 conversion: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during M4A to MP3 conversion: {e}")
    
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
            print(f"Step 1: Converting {input_file} to M4A...")
            self.mp4_to_m4a(input_file, m4a_file)
            
            # Step 2: Convert M4A to MP3
            print(f"Step 2: Converting {m4a_file} to MP3...")
            result = self.m4a_to_mp3(m4a_file, output_file)
            
            # Clean up intermediate file if requested
            if not keep_intermediate:
                try:
                    os.remove(m4a_file)
                    print(f"Cleaned up intermediate file: {m4a_file}")
                except OSError as e:
                    print(f"Warning: Could not remove intermediate file {m4a_file}: {e}")
            
            return result
            
        except Exception as e:
            # Clean up intermediate file on error
            if os.path.exists(m4a_file) and not keep_intermediate:
                try:
                    os.remove(m4a_file)
                except OSError:
                    pass
            raise e


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
    print("  mp4_converter.exe                    - Convert all MP4 files in current directory")
    print("  mp4_converter.exe <input_file>       - Convert specific MP4 file")
    print("  mp4_converter.exe --help             - Show this help message")
    print()
    print("Options:")
    print("  --keep-intermediate    Keep intermediate M4A files (default: delete them)")
    print("  --m4a-only            Only convert to M4A format")
    print("  --mp3-only            Only convert to MP3 format (via M4A)")
    print()


def main():
    """Main function for the PoC CLI"""
    print_banner()
    
    # Parse command line arguments
    args = sys.argv[1:]
    keep_intermediate = "--keep-intermediate" in args
    m4a_only = "--m4a-only" in args
    mp3_only = "--mp3-only" in args
    
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
            print(f"Error: File '{args[0]}' not found!")
            sys.exit(1)
    else:
        # Process all MP4 files in current directory
        current_dir = os.getcwd()
        input_files = find_mp4_files(current_dir)
        
        if not input_files:
            print("No MP4 files found in the current directory.")
            print(f"Current directory: {current_dir}")
            print("\nSupported file extensions: .mp4, .MP4")
            return
    
    print(f"Found {len(input_files)} MP4 file(s) to process:")
    for i, file in enumerate(input_files, 1):
        print(f"  {i}. {os.path.basename(file)}")
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
            if m4a_only:
                # Convert only to M4A
                m4a_output = converter.mp4_to_m4a(input_file)
                print(f"✓ M4A conversion completed: {os.path.basename(m4a_output)}")
                
            elif mp3_only:
                # Convert directly to MP3 (via M4A)
                mp3_output = converter.convert_mp4_to_mp3(input_file, keep_intermediate=keep_intermediate)
                print(f"✓ MP3 conversion completed: {os.path.basename(mp3_output)}")
                
            else:
                # Convert to both M4A and MP3 (default)
                m4a_output = converter.mp4_to_m4a(input_file)
                print(f"✓ M4A conversion completed: {os.path.basename(m4a_output)}")
                
                mp3_output = converter.m4a_to_mp3(m4a_output)
                print(f"✓ MP3 conversion completed: {os.path.basename(mp3_output)}")
                
                # Clean up intermediate M4A file if not requested to keep
                if not keep_intermediate:
                    try:
                        os.remove(m4a_output)
                        print(f"✓ Cleaned up intermediate file: {os.path.basename(m4a_output)}")
                    except OSError as e:
                        print(f"⚠ Warning: Could not remove {m4a_output}: {e}")
            
            successful_conversions += 1
            print(f"✓ Successfully processed: {file_name}")
            
        except Exception as e:
            failed_conversions += 1
            print(f"✗ Error processing {file_name}: {e}")
        
        print()
    
    # Print summary
    print("=" * 60)
    print("                    CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Total files processed:     {total_files}")
    print(f"Successful conversions:    {successful_conversions}")
    print(f"Failed conversions:        {failed_conversions}")
    
    if failed_conversions == 0:
        print("\n🎉 All conversions completed successfully!")
    else:
        print(f"\n⚠ {failed_conversions} conversion(s) failed. Check the error messages above.")
    
    print("\nPress any key to exit...")
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