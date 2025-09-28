"""
MP4 to Text Converter - Enhanced PoC with Local Whisper
Combined script with converter functionality, CLI interface, and speech-to-text processing

This PoC processes MP4 files, converts them to audio formats, and transcribes them to text
using local Whisper AI with progress tracking and interactive format selection.
"""

import os
import sys
import glob
import warnings

# Suppress specific Triton warnings from Whisper timing operations
# These warnings are cosmetic - GPU transcription still works at full speed
# Only timing alignment operations fall back to CPU (minimal performance impact)
warnings.filterwarnings("ignore", category=UserWarning, module="whisper.timing")
warnings.filterwarnings("ignore", message="Failed to launch Triton kernels")
warnings.filterwarnings("ignore", message=".*DTW implementation.*")

import ffmpeg
import subprocess
import threading
import time
import re
import tempfile
import shutil
import json
from pathlib import Path
from typing import List, Tuple, Optional

# Whisper and AI dependencies
try:
    import whisper
    import torch
    import torchaudio
    import numpy as np
    import soundfile as sf
    WHISPER_AVAILABLE = True
except ImportError as e:
    WHISPER_AVAILABLE = False
    # Note: Error details will be shown when actually needed


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


class AudioSplitter:
    """Audio file splitting functionality for large files"""
    
    def __init__(self, max_chunk_size_mb: float = 20.0):
        """Initialize audio splitter
        
        Args:
            max_chunk_size_mb: Maximum size of each chunk in MB (default 20MB for Whisper)
        """
        self.max_chunk_size_mb = max_chunk_size_mb
        self.temp_dir = None
    
    def get_audio_duration(self, audio_file: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            probe = ffmpeg.probe(audio_file)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception:
            try:
                cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                       '-of', 'csv=p=0', audio_file]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return float(result.stdout.strip())
            except Exception:
                return 0
    
    def calculate_chunk_duration(self, audio_file: str) -> float:
        """Calculate optimal chunk duration to stay under size limit"""
        try:
            # Get file size and duration
            file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
            total_duration = self.get_audio_duration(audio_file)
            
            if file_size_mb <= self.max_chunk_size_mb:
                return total_duration  # No splitting needed
            
            # Calculate chunk duration to achieve target size
            chunks_needed = file_size_mb / self.max_chunk_size_mb
            chunk_duration = total_duration / chunks_needed
            
            # Add small buffer and round to reasonable interval
            chunk_duration = max(60, chunk_duration * 0.9)  # At least 1 minute chunks
            return chunk_duration
            
        except Exception as e:
            print(f"Warning: Could not calculate optimal chunk size: {e}")
            return 1200  # Default 20 minutes
    
    def split_audio_file(self, input_file: str) -> List[str]:
        """Split audio file into chunks and return list of chunk paths"""
        input_path = Path(input_file)
        
        # Create temporary directory for chunks
        self.temp_dir = tempfile.mkdtemp(prefix="audio_chunks_")
        
        # Calculate chunk duration
        chunk_duration = self.calculate_chunk_duration(input_file)
        total_duration = self.get_audio_duration(input_file)
        
        if total_duration <= chunk_duration:
            # No splitting needed, copy original file
            chunk_file = os.path.join(self.temp_dir, f"chunk_000.{input_path.suffix[1:]}")
            shutil.copy2(input_file, chunk_file)
            return [chunk_file]
        
        print(f"  📂 Splitting audio file into chunks...")
        print(f"  ⏱️ Total duration: {total_duration/60:.1f} minutes")
        print(f"  ✂️ Chunk duration: {chunk_duration/60:.1f} minutes")
        
        chunk_files = []
        chunk_index = 0
        start_time = 0
        
        while start_time < total_duration:
            chunk_file = os.path.join(self.temp_dir, f"chunk_{chunk_index:03d}.{input_path.suffix[1:]}")
            
            # Calculate end time for this chunk
            end_time = min(start_time + chunk_duration, total_duration)
            
            try:
                # Use FFmpeg to extract chunk
                cmd = [
                    'ffmpeg', '-y',
                    '-i', str(input_path),
                    '-ss', str(start_time),
                    '-t', str(end_time - start_time),
                    '-c', 'copy',  # Copy without re-encoding for speed
                    '-v', 'quiet',
                    chunk_file
                ]
                
                subprocess.run(cmd, check=True)
                chunk_files.append(chunk_file)
                
                print(f"    ✅ Chunk {chunk_index + 1}: {start_time/60:.1f}m - {end_time/60:.1f}m")
                
                start_time = end_time
                chunk_index += 1
                
            except subprocess.CalledProcessError as e:
                print(f"    ❌ Failed to create chunk {chunk_index}: {e}")
                break
        
        print(f"  🎵 Created {len(chunk_files)} audio chunks")
        return chunk_files
    
    def cleanup_temp_files(self):
        """Clean up temporary chunk files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"  🧹 Cleaned up temporary files")
            except Exception as e:
                print(f"  ⚠️ Warning: Could not clean up temp files: {e}")


class WhisperTranscriber:
    """Local Whisper AI transcription with GPU support"""
    
    def __init__(self, model_name: str = "large-v3", device: str = "auto"):
        """Initialize Whisper transcriber
        
        Args:
            model_name: Whisper model to use (large-v3 recommended for Korean)
            device: Device to use ('auto', 'cuda', 'cpu')
        """
        self.model_name = model_name
        self.model = None
        self.device = self._setup_device(device)
        
        if not WHISPER_AVAILABLE:
            raise ImportError("Whisper is not available. Install with: pip install openai-whisper torch")
    
    def _setup_device(self, device: str) -> str:
        """Setup optimal device for inference"""
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"  🚀 GPU detected: {gpu_name} ({gpu_memory:.1f}GB VRAM)")
                print(f"  ⚡ Using GPU acceleration for faster processing")
            else:
                device = "cpu"
                print(f"  💻 No GPU detected, using CPU for processing")
                print(f"  ⚠️  CPU processing will be significantly slower")
        else:
            print(f"  🎯 Using specified device: {device}")
        
        return device
    
    def load_model(self):
        """Load Whisper model (downloads if first time)"""
        if self.model is None:
            print(f"  📥 Loading Whisper {self.model_name} model...")
            print(f"  ℹ️ First run may download ~3GB model file")
            
            try:
                # Load with optimized settings for Windows/CUDA
                self.model = whisper.load_model(
                    self.model_name, 
                    device=self.device,
                    download_root=None,  # Use default cache
                    in_memory=True  # Keep model in memory for better performance
                )
                print(f"  ✅ Model loaded successfully on {self.device}")
                
                # Note: Removed pre-warming to avoid language detection issues
                if self.device == "cuda":
                    print(f"  🔥 GPU model ready for Korean transcription")
                
            except Exception as e:
                print(f"  ❌ Failed to load model: {e}")
                raise
    
    def transcribe_chunk(self, audio_file: str, chunk_index: int, start_time: float = 0, language: str = "ko") -> dict:
        """Transcribe a single audio chunk"""
        try:
            print(f"    🎤 Processing chunk {chunk_index + 1}...")
            
            # Temporarily suppress timing-related warnings during transcription
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="whisper.timing")
                warnings.filterwarnings("ignore", message="Failed to launch Triton kernels")
                warnings.filterwarnings("ignore", message=".*DTW implementation.*")
                
                # Transcribe with FORCED Korean language and anti-hallucination settings
                result = self.model.transcribe(
                    audio_file,
                    language=language,  # Use the forced language parameter
                    task="transcribe",
                    fp16=torch.cuda.is_available(),  # Use FP16 for GPU acceleration
                    verbose=False,
                    # Disable word-level timestamps to avoid Triton kernel warnings
                    word_timestamps=False,  # Disabled to prevent Triton warnings
                    # Remove initial_prompt to prevent contamination of output
                    # initial_prompt removed to prevent contamination
                    no_speech_threshold=0.05,  # Very low threshold to catch quiet beginnings
                    logprob_threshold=-1.0,  # Lower threshold for better accuracy with quiet audio
                    compression_ratio_threshold=1.8,  # Lower to reduce hallucinations like "자막제공자"
                    condition_on_previous_text=False,  # Disable to prevent prompt contamination
                    temperature=0.0,  # Deterministic output for consistency
                    beam_size=1,  # Disable beam search to avoid some GPU optimization issues
                    # Anti-hallucination settings
                    suppress_tokens=[-1],  # Suppress common subtitle tokens
                    without_timestamps=True  # Focus on content, not timing precision
                )
            
            # Adjust timestamps based on chunk start time
            if start_time > 0:
                for segment in result.get("segments", []):
                    segment["start"] += start_time
                    segment["end"] += start_time
            
            # Clean up any prompt contamination and subtitle hallucinations from the output text
            if "text" in result:
                cleaned_text = result["text"]
                
                # Remove common prompt contaminations
                prompt_phrases = [
                    "한국어 음성을 정확하게 인식해주세요.",
                    "안녕하세요.",
                    "한국어 음성을 정확하게 인식해주세요",
                    "안녕하세요"
                ]
                
                # Remove common subtitle hallucinations
                subtitle_hallucinations = [
                    "자막제공자",
                    "자막 제공자",
                    "자막제공", 
                    "자막 제공",
                    "구독",
                    "좋아요",
                    "알림",
                    "구독과 좋아요",
                    "시청해주셔서 감사합니다",
                    "채널 구독",
                    "Subscribe",
                    "Like"
                ]
                
                # Clean all unwanted phrases
                all_unwanted = prompt_phrases + subtitle_hallucinations
                for phrase in all_unwanted:
                    cleaned_text = cleaned_text.replace(phrase, "").strip()
                
                # Clean up multiple spaces and normalize
                import re
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                
                result["text"] = cleaned_text
            
            return result
            
        except Exception as e:
            print(f"    ❌ Error transcribing chunk {chunk_index + 1}: {e}")
            return {"text": f"[Error transcribing chunk {chunk_index + 1}: {e}]", "segments": []}
    
    def transcribe_chunks(self, chunk_files: List[str], chunk_duration: float, language: str = "ko") -> List[dict]:
        """Transcribe multiple audio chunks"""
        if not self.model:
            self.load_model()
        
        results = []
        total_chunks = len(chunk_files)
        
        print(f"  🎯 Transcribing {total_chunks} chunks with Whisper {self.model_name}")
        
        for i, chunk_file in enumerate(chunk_files):
            start_time = i * chunk_duration
            result = self.transcribe_chunk(chunk_file, i, start_time, language)
            results.append(result)
            
            # Show progress
            progress = ((i + 1) / total_chunks) * 100
            print(f"    📊 Progress: {progress:.1f}% ({i + 1}/{total_chunks})")
        
        return results
    
    def merge_transcripts(self, results: List[dict]) -> str:
        """Merge multiple chunk transcripts into single text"""
        merged_text = []
        
        for i, result in enumerate(results):
            chunk_text = result.get("text", "").strip()
            if chunk_text:
                # Add chunk separator for debugging (optional)
                if len(results) > 1 and i > 0:
                    merged_text.append(f"\n")
                merged_text.append(chunk_text)
        
        return " ".join(merged_text).strip()
    
    def transcribe_audio_file(self, audio_file: str, output_file: str = None, language: str = "ko") -> str:
        """Complete transcription pipeline for audio file"""
        input_path = Path(audio_file)
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = str(input_path.with_suffix('.txt'))
        
        print(f"  🎵 Starting transcription: {input_path.name}")
        
        # Initialize splitter
        splitter = AudioSplitter()
        
        try:
            # Split audio file
            chunk_files = splitter.split_audio_file(audio_file)
            
            # Calculate chunk duration for timestamp adjustment
            total_duration = splitter.get_audio_duration(audio_file)
            chunk_duration = total_duration / len(chunk_files) if len(chunk_files) > 1 else 0
            
            # Transcribe chunks
            results = self.transcribe_chunks(chunk_files, chunk_duration, language)
            
            # Merge results
            final_transcript = self.merge_transcripts(results)
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_transcript)
            
            print(f"  ✅ Transcription completed: {os.path.basename(output_file)}")
            print(f"  📝 Text length: {len(final_transcript)} characters")
            
            return output_file
            
        except Exception as e:
            print(f"  ❌ Transcription failed: {e}")
            raise
        finally:
            # Clean up temporary files
            splitter.cleanup_temp_files()
            
            # Clear GPU memory if using CUDA
            if self.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()
                print(f"  🧹 GPU memory cleared")


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
    
    def transcribe_audio_to_text(self, audio_file: str, output_file: str = None, force_language: str = "ko") -> str:
        """
        Transcribe audio file to text using local Whisper AI with forced Korean language
        
        Args:
            audio_file (str): Path to the input audio file (M4A, MP3, WAV)
            output_file (str, optional): Path to the output text file.
                                       If None, will use input filename with .txt extension
            force_language (str): Language code to force recognition (default: "ko" for Korean)
        
        Returns:
            str: Path to the generated text file
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If transcription fails
        """
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper AI is not available. Please install with: pip install openai-whisper torch")
        
        input_path = Path(audio_file)
        
        # Check if input file exists
        if not input_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = str(input_path.with_suffix('.txt'))
        
        try:
            print(f"  🤖 Starting AI transcription with Whisper large-v3...")
            print(f"  🎵 Input: {os.path.basename(audio_file)}")
            print(f"  📝 Output: {os.path.basename(output_file)}")
            
            # Initialize Whisper transcriber
            transcriber = WhisperTranscriber(model_name="large-v3", device="auto")
            
            # Perform transcription with forced Korean
            result_file = transcriber.transcribe_audio_file(audio_file, output_file, force_language)
            
            print(f"  🎉 Transcription completed successfully!")
            return result_file
            
        except Exception as e:
            raise RuntimeError(f"Error during audio transcription: {e}")


def find_audio_files(directory: str = ".") -> list:
    """
    Find all audio files in the specified directory
    
    Args:
        directory (str): Directory to search for audio files (defaults to current directory)
    
    Returns:
        list: List of audio file paths (M4A, MP3, WAV)
    """
    patterns = ["*.m4a", "*.M4A", "*.mp3", "*.MP3", "*.wav", "*.WAV"]
    audio_files = []
    
    for pattern in patterns:
        search_path = os.path.join(directory, pattern)
        audio_files.extend(glob.glob(search_path))
    
    return sorted(list(set(audio_files)))  # Remove duplicates and sort


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
    print("         MP4 to Text Converter - Enhanced PoC")
    print("         MP4 → Audio → Text with Local Whisper AI")
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
    print("  --transcribe          Convert MP4 to text using Whisper AI")
    print()


def select_workflow_type(file_count: int = 1) -> str:
    """
    Interactive workflow selection menu
    
    Args:
        file_count: Number of files to process (for batch processing info)
    
    Returns:
        str: workflow type ('audio-only', 'text-only', 'audio-and-text')
    """
    print("🚀 Workflow Selection")
    print("=" * 25)
    
    if file_count > 1:
        print(f"📁 Found {file_count} MP4 files - This selection will apply to ALL files")
        print()
    
    print("1. Convert to Audio Only (MP3/M4A)")
    print("2. Convert to Text Only (using Whisper AI)")
    print("3. Convert to Both Audio and Text")
    print()
    
    while True:
        try:
            if file_count > 1:
                choice = input(f"Select workflow for ALL {file_count} files (1-3): ").strip()
            else:
                choice = input("Select workflow (1-3): ").strip()
                
            if choice == "1":
                return "audio-only"
            elif choice == "2":
                return "text-only"
            elif choice == "3":
                return "audio-and-text"
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def select_output_format(file_count: int = 1) -> tuple:
    """
    Interactive format selection menu for audio conversion
    
    Args:
        file_count: Number of files to process (for batch processing info)
    
    Returns:
        tuple: (format_choice, keep_intermediate)
               format_choice: 'm4a', 'mp3', 'both'
               keep_intermediate: bool
    """
    print("\n🎵 Audio Format Selection")
    print("=" * 30)
    
    if file_count > 1:
        print(f"📁 This format selection will apply to ALL {file_count} files")
        print()
    
    print("1. MP3 only (fastest, direct conversion)")
    print("2. M4A only (high quality, smaller size)")
    print("3. Both MP3 and M4A (recommended)")
    print()
    
    while True:
        try:
            if file_count > 1:
                choice = input(f"Select audio format for ALL {file_count} files (1-3): ").strip()
            else:
                choice = input("Select audio format (1-3): ").strip()
                
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


def confirm_workflow(input_files: list, workflow_type: str, format_choice: str = None, keep_intermediate: bool = False) -> bool:
    """
    Show workflow summary and ask for confirmation
    
    Args:
        input_files: List of input files
        workflow_type: Type of workflow ('audio-only', 'text-only', 'audio-and-text')
        format_choice: Selected audio format (if applicable)
        keep_intermediate: Whether to keep intermediate files
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    print("\n📋 Batch Processing Summary")
    print("=" * 30)
    print(f"📁 Files to process: {len(input_files)}")
    
    if len(input_files) <= 5:
        # Show all files if 5 or fewer
        for i, file in enumerate(input_files, 1):
            print(f"  {i}. {os.path.basename(file)}")
    else:
        # Show first 3 and last 2 if more than 5
        for i in range(3):
            print(f"  {i+1}. {os.path.basename(input_files[i])}")
        print(f"  ... ({len(input_files)-5} more files)")
        for i in range(len(input_files)-2, len(input_files)):
            print(f"  {i+1}. {os.path.basename(input_files[i])}")
    
    print()
    print(f"🎯 Workflow: {workflow_type.replace('-', ' ').title()}")
    
    if workflow_type == "audio-only":
        format_descriptions = {
            'mp3': "MP3 format only (direct conversion)",
            'm4a': "M4A format only",
            'both': f"Both M4A and MP3 formats {'(keeping M4A)' if keep_intermediate else '(removing intermediate M4A)'}"
        }
        print(f"📄 Output: {format_descriptions[format_choice]}")
        
    elif workflow_type == "text-only":
        print(f"📄 Output: Text files (.txt) using Whisper AI large-v3 model")
        if WHISPER_AVAILABLE:
            print(f"🤖 AI Model: Local Whisper with {'GPU' if torch.cuda.is_available() else 'CPU'} acceleration")
        else:
            print(f"⚠️  Warning: Whisper AI not installed")
            
    elif workflow_type == "audio-and-text":
        format_descriptions = {
            'mp3': "MP3 + Text files",
            'm4a': "M4A + Text files", 
            'both': f"Both M4A and MP3 + Text files {'(keeping M4A)' if keep_intermediate else '(removing intermediate M4A)'}"
        }
        print(f"📄 Output: {format_descriptions[format_choice]}")
        if WHISPER_AVAILABLE:
            print(f"🤖 AI Model: Local Whisper with {'GPU' if torch.cuda.is_available() else 'CPU'} acceleration")
    
    print()
    
    if len(input_files) > 1:
        print(f"⚡ Batch Mode: All {len(input_files)} files will be processed automatically")
        print(f"⏱️  Estimated time: {'Long processing time for text conversion' if 'text' in workflow_type else 'Moderate processing time'}")
        print()
    
    while True:
        try:
            confirm = input("Proceed with processing? (y/n): ").strip().lower()
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
    """Main function for the Enhanced PoC with Audio-to-Text capabilities"""
    print_banner()
    
    # Parse command line arguments
    args = sys.argv[1:]
    keep_intermediate_flag = "--keep-intermediate" in args
    m4a_only_flag = "--m4a-only" in args
    mp3_only_flag = "--mp3-only" in args
    both_flag = "--both" in args
    transcribe_flag = "--transcribe" in args
    
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
        # Check for batch processing directory first
        input_dir = os.path.join(os.getcwd(), "run", "input")
        if os.path.exists(input_dir):
            input_files = find_mp4_files(input_dir)
            if input_files:
                print(f"📁 Found {len(input_files)} MP4 files in batch input directory")
                print(f"📂 Input directory: {input_dir}")
            else:
                # Fall back to current directory
                current_dir = os.getcwd()
                input_files = find_mp4_files(current_dir)
        else:
            # Process all MP4 files in current directory
            current_dir = os.getcwd()
            input_files = find_mp4_files(current_dir)
        
        if not input_files:
            print("No MP4 files found.")
            if os.path.exists(input_dir):
                print(f"Checked directories:")
                print(f"  - Batch input: {input_dir}")
                print(f"  - Current: {os.getcwd()}")
            else:
                print(f"Current directory: {os.getcwd()}")
            print("\nSupported file extensions: .mp4, .MP4")
            print("\n💡 Tip: Place your MP4 files in:")
            print("   - run\\input\\ directory (for batch processing)")
            print("   - Same directory as this executable")
            return
    
    # Determine workflow and settings
    if m4a_only_flag or mp3_only_flag or both_flag or transcribe_flag:
        # Command-line mode (skip interactive selection)
        if transcribe_flag:
            workflow_type = "text-only"
            format_choice = None
            keep_intermediate = False
        elif m4a_only_flag:
            workflow_type = "audio-only"
            format_choice = "m4a"
            keep_intermediate = False
        elif mp3_only_flag:
            workflow_type = "audio-only"
            format_choice = "mp3"
            keep_intermediate = False
        elif both_flag:
            workflow_type = "audio-only"
            format_choice = "both"
            keep_intermediate = keep_intermediate_flag
        else:
            workflow_type = "audio-only"  # Default
            format_choice = "both"
            keep_intermediate = keep_intermediate_flag
    else:
        # Interactive mode
        total_files = len(input_files)
        workflow_type = select_workflow_type(total_files)
        
        if workflow_type == "audio-only":
            format_choice, keep_intermediate = select_output_format(total_files)
        elif workflow_type == "text-only":
            format_choice = None
            keep_intermediate = False
        elif workflow_type == "audio-and-text":
            format_choice, keep_intermediate = select_output_format(total_files)
        
        # Show confirmation
        if not confirm_workflow(input_files, workflow_type, format_choice, keep_intermediate):
            print("❌ Processing cancelled by user.")
            return
    
    # Start processing
    print("🚀 Starting Processing Pipeline")
    print("=" * 35)
    print()
    
    # Check Whisper availability if needed
    if workflow_type in ["text-only", "audio-and-text"] and not WHISPER_AVAILABLE:
        print("❌ Error: Whisper AI is not available.")
        print("Please install with: pip install openai-whisper torch")
        return
    
    # Process each file
    total_files = len(input_files)
    successful_conversions = 0
    failed_conversions = 0
    start_time = time.time()
    
    if total_files > 1:
        print(f"🔄 Batch Processing: {total_files} files with same settings")
        print("=" * 50)
    
    for i, input_file in enumerate(input_files, 1):
        input_path = Path(input_file)
        file_name = input_path.name
        
        # Show batch progress with time estimates
        if total_files > 1:
            elapsed = time.time() - start_time
            if i > 1:  # Can estimate time after first file
                avg_time_per_file = elapsed / (i - 1)
                remaining_files = total_files - i + 1
                estimated_remaining = avg_time_per_file * remaining_files
                eta_minutes = int(estimated_remaining / 60)
                eta_seconds = int(estimated_remaining % 60)
                print(f"📊 Batch Progress: [{i}/{total_files}] | ETA: {eta_minutes}m {eta_seconds}s")
            else:
                print(f"📊 Batch Progress: [{i}/{total_files}] | Calculating ETA...")
        else:
            print(f"[{i}/{total_files}]", end=" ")
            
        print(f"Processing: {file_name}")
        print("-" * 50)
        
        try:
            audio_file = None  # Track intermediate audio file for text conversion
            
            # Step 1: Audio conversion (if needed)
            if workflow_type in ["audio-only", "audio-and-text"]:
                if format_choice == "m4a":
                    # Convert only to M4A
                    audio_file = converter.mp4_to_m4a(input_file)
                    print(f"✅ M4A conversion completed: {os.path.basename(audio_file)}")
                    
                elif format_choice == "mp3":
                    # Convert directly to MP3
                    audio_file = converter.convert_mp4_to_mp3_direct(input_file)
                    print(f"✅ MP3 conversion completed: {os.path.basename(audio_file)}")
                    
                elif format_choice == "both":
                    # Convert to both M4A and MP3
                    m4a_file = converter.mp4_to_m4a(input_file)
                    print(f"✅ M4A conversion completed: {os.path.basename(m4a_file)}")
                    
                    mp3_file = converter.convert_mp4_to_mp3_direct(input_file)
                    print(f"✅ MP3 conversion completed: {os.path.basename(mp3_file)}")
                    
                    # Use M4A for text conversion (better quality)
                    audio_file = m4a_file
                    
                    # Clean up intermediate M4A file if not requested to keep
                    if not keep_intermediate and workflow_type == "audio-only":
                        try:
                            os.remove(m4a_file)
                            print(f"🧹 Cleaned up intermediate file: {os.path.basename(m4a_file)}")
                        except OSError as e:
                            print(f"⚠ Warning: Could not remove {m4a_file}: {e}")
            
            # Step 2: Text conversion (if needed)
            if workflow_type in ["text-only", "audio-and-text"]:
                if workflow_type == "text-only":
                    # Convert MP4 to audio first (use M4A for best quality)
                    print(f"  🎵 Converting to audio for transcription...")
                    audio_file = converter.mp4_to_m4a(input_file)
                
                # Transcribe to text
                print(f"  🤖 Starting AI transcription...")
                text_file = converter.transcribe_audio_to_text(audio_file)
                print(f"✅ Text transcription completed: {os.path.basename(text_file)}")
                
                # Clean up temporary audio file for text-only workflow
                if workflow_type == "text-only":
                    try:
                        os.remove(audio_file)
                        print(f"🧹 Cleaned up temporary audio file: {os.path.basename(audio_file)}")
                    except OSError as e:
                        print(f"⚠ Warning: Could not remove temporary file: {e}")
            
            successful_conversions += 1
            print(f"🎉 Successfully processed: {file_name}")
            
        except Exception as e:
            failed_conversions += 1
            print(f"❌ Error processing {file_name}: {e}")
        
        print()
    
    # Calculate total processing time
    total_time = time.time() - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    
    # Print summary
    print("=" * 60)
    if total_files > 1:
        print("                  🚀 BATCH PROCESSING SUMMARY 🚀")
    else:
        print("                    🎵 PROCESSING SUMMARY 🎵")
    print("=" * 60)
    print(f"Total files processed:     {total_files}")
    print(f"Successful conversions:    {successful_conversions}")
    print(f"Failed conversions:        {failed_conversions}")
    
    # Show timing information
    if hours > 0:
        print(f"Total processing time:     {hours}h {minutes}m {seconds}s")
    else:
        print(f"Total processing time:     {minutes}m {seconds}s")
    
    if total_files > 1 and successful_conversions > 0:
        avg_time = total_time / successful_conversions
        avg_minutes = int(avg_time // 60)
        avg_seconds = int(avg_time % 60)
        print(f"Average time per file:     {avg_minutes}m {avg_seconds}s")
    
    # Auto-move text files to output directory if using batch processing
    input_dir = os.path.join(os.getcwd(), "run", "input")
    output_dir = os.path.join(os.getcwd(), "run", "output")
    
    if (len(input_files) > 0 and 
        os.path.exists(input_dir) and 
        any(input_file.startswith(input_dir) for input_file in input_files) and
        workflow_type in ["text-only", "audio-and-text"]):
        
        # Move text files to output directory
        os.makedirs(output_dir, exist_ok=True)
        moved_files = 0
        
        for txt_file in glob.glob("*.txt"):
            try:
                output_path = os.path.join(output_dir, txt_file)
                os.rename(txt_file, output_path)
                moved_files += 1
            except Exception as e:
                print(f"⚠️ Could not move {txt_file} to output directory: {e}")
        
        if moved_files > 0:
            print(f"\n📁 Moved {moved_files} text file(s) to: {output_dir}")
    
    if failed_conversions == 0:
        print("\n🎉 All batch processing completed successfully!")
        if total_files > 1:
            print(f"📁 {successful_conversions} files processed automatically!")
        if workflow_type in ["text-only", "audio-and-text"]:
            print("🤖 AI transcription results are ready!")
        print("✨ Your files are ready to use!")
    else:
        print(f"\n⚠ {failed_conversions} processing task(s) failed. Check the error messages above.")
        if successful_conversions > 0:
            print(f"✅ {successful_conversions} files were processed successfully.")
    
    # Show appropriate directory information
    if (os.path.exists(output_dir) and 
        workflow_type in ["text-only", "audio-and-text"] and
        any(input_file.startswith(input_dir) for input_file in input_files if os.path.exists(input_dir))):
        print(f"\n📁 Check your text files in: {output_dir}")
    else:
        print("\n📁 Check your files in the current directory.")
        
    print("\nPress Enter to exit...")
    try:
        input()
    except KeyboardInterrupt:
        pass
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