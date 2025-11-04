#!/usr/bin/env python
"""
Pre-download ML models during build phase to avoid runtime OOM
This downloads models to cache, so they don't need to be downloaded when app starts
"""

import os
import sys

print("=" * 60)
print("  Pre-downloading ML Models for Chatbot")
print("=" * 60)
print()

# 1. Download Sentence Transformer model
print("📦 Downloading Sentence Transformer model...")
print("   Model: paraphrase-multilingual-MiniLM-L12-v2 (~420MB)")
print()

try:
    from sentence_transformers import SentenceTransformer

    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    model = SentenceTransformer(model_name)

    print(f"✅ Successfully downloaded: {model_name}")
    print(f"   Cached at: {model.cache_folder}")
    print()

except Exception as e:
    print(f"❌ Failed to download sentence transformer: {e}")
    sys.exit(1)

# 2. Verify ChromaDB is importable
print("📦 Verifying ChromaDB installation...")
try:
    import chromadb
    print("✅ ChromaDB ready")
    print()
except Exception as e:
    print(f"❌ ChromaDB import failed: {e}")
    sys.exit(1)

# 3. Verify Google Generative AI
print("📦 Verifying Google Generative AI...")
try:
    import google.generativeai as genai
    print("✅ Google Generative AI ready")
    print()
except Exception as e:
    print(f"❌ Google Generative AI import failed: {e}")
    sys.exit(1)

print("=" * 60)
print("✅ All ML models downloaded and ready!")
print("=" * 60)
print()
print("Benefits:")
print("  • Models cached on disk")
print("  • No runtime download → Faster startup")
print("  • Lower RAM usage → No OOM crashes")
print()
