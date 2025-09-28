#!/usr/bin/env python3
"""Quick Whisper Test - Check if warnings are suppressed"""

import warnings
import os

# Suppress Triton kernel warnings
warnings.filterwarnings("ignore", message="Failed to launch Triton kernels")
warnings.filterwarnings("ignore", message=".*Triton.*", category=UserWarning)

print("=== Quick Whisper Test ===")

try:
    import whisper
    import torch
    
    print(f"Whisper available: ✅")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        
        # Quick model load test
        print("\n📥 Loading tiny model for quick test...")
        model = whisper.load_model("tiny", device="cuda")
        print("✅ Model loaded successfully")
        
        # Test with a very short dummy audio (silence)
        print("🎤 Testing transcription with tiny model...")
        import numpy as np
        
        # Create 1 second of silence (16kHz sample rate)
        dummy_audio = np.zeros(16000, dtype=np.float32)
        
        result = model.transcribe(dummy_audio, language="ko", verbose=False)
        print(f"✅ Test transcription completed")
        print(f"Result: '{result.get('text', '').strip()}'")
        
        # Clean up GPU memory
        del model
        torch.cuda.empty_cache()
        print("🧹 GPU memory cleared")
        
    else:
        print("⚠️ No GPU available")
    
except ImportError as e:
    print(f"❌ Whisper not available: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")

print("\n" + "="*50)
input("Press Enter to exit...")