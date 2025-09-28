"""
MP4 to Text Converter Engine
Core module for audio format conversion using FFmpeg
"""

import os
import sys
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


def main():
    """Main function for testing the converter"""
    converter = AudioConverter()
    
    # Example usage
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        try:
            result = converter.convert_mp4_to_mp3(input_file)
            print(f"Conversion completed: {result}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python converter.py <input_mp4_file>")
        sys.exit(1)


if __name__ == "__main__":
    main()