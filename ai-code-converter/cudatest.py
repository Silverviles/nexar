# test_gpu.py
import torch
import sys

print("="*50)
print("GPU DETECTION TEST")
print("="*50)

# Test 1: Basic CUDA availability
print(f"\n1. CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    # Test 2: Get GPU name
    print(f"\n2. GPU Name: {torch.cuda.get_device_name(0)}")
    
    # Test 3: Check CUDA version
    print(f"\n3. PyTorch CUDA version: {torch.version.cuda}")
    
    # Test 4: Simple tensor operation on GPU
    print("\n4. Testing tensor operation on GPU...")
    x = torch.tensor([1.0, 2.0, 3.0]).cuda()
    y = torch.tensor([4.0, 5.0, 6.0]).cuda()
    z = x + y
    print(f"   Result (should be [5, 7, 9]): {z}")
    print(f"   Tensor device: {z.device}")
    
    # Test 5: Memory info
    print(f"\n5. GPU Memory:")
    print(f"   Allocated: {torch.cuda.memory_allocated(0)/1024**2:.2f} MB")
    print(f"   Cached: {torch.cuda.memory_reserved(0)/1024**2:.2f} MB")
    
    print("\n✅ GPU IS WORKING! Your training will use the RTX 3050")
else:
    print("\n❌ GPU NOT DETECTED by PyTorch")
    print("\nTroubleshooting info:")
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    
print("\n" + "="*50)