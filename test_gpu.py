#!/usr/bin/env python3
"""GPU Detection Test Script"""

import sys
import os

try:
    import torch
    print("=== PyTorch GPU Detection Test ===")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"GPU {i}: {props.name}")
            print(f"  Memory: {props.total_memory / 1024**3:.1f} GB")
            print(f"  Compute capability: {props.major}.{props.minor}")
    else:
        print("No GPU detected or CUDA not available")
        print("Possible issues:")
        print("- CUDA drivers not installed")
        print("- CUDA version mismatch with PyTorch")
        print("- GPU not compatible")
    
    print("\n=== Environment Info ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Test a simple tensor operation
    try:
        if torch.cuda.is_available():
            print("\n=== GPU Test ===")
            device = torch.device("cuda")
            x = torch.randn(1000, 1000).to(device)
            y = torch.randn(1000, 1000).to(device)
            z = torch.mm(x, y)
            print("✅ GPU tensor operations working correctly")
            print(f"Result tensor shape: {z.shape}")
            print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
        else:
            print("\n⚠️ No GPU available for testing")
    except Exception as e:
        print(f"\n❌ GPU test failed: {e}")

except ImportError as e:
    print(f"❌ PyTorch not available: {e}")
    print("Install with: pip install torch torchaudio")

print("\n" + "="*50)
input("Press Enter to exit...")