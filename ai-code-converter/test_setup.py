# Test Python
print("✅ Python is working!")

# Test Qiskit
try:
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    print("✅ Qiskit is installed!")
except:
    print("❌ Qiskit failed to import")

# Test Transformers
try:
    import transformers
    print("✅ Transformers is installed!")
except:
    print("❌ Transformers failed to import")

# Test Torch
try:
    import torch
    print("✅ PyTorch is installed!")
except:
    print("❌ PyTorch failed to import")

print("\n🎉 Setup complete!")