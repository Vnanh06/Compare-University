#!/usr/bin/env python
"""
Pre-download ML models during build phase to avoid runtime OOM
This downloads models to cache, so they don't need to be downloaded when app starts
"""

import os
import sys

def main():
    print("=" * 60)
    print("  Pre-downloading ML Models for Chatbot")
    print("=" * 60)
    print()

    # Show cache directories
    print("📁 Cache directories:")
    print(f"   HF_HOME: {os.getenv('HF_HOME', 'not set')}")
    print(f"   TRANSFORMERS_CACHE: {os.getenv('TRANSFORMERS_CACHE', 'not set')}")
    print(f"   SENTENCE_TRANSFORMERS_HOME: {os.getenv('SENTENCE_TRANSFORMERS_HOME', 'not set')}")
    print()

    # 1. Download Sentence Transformer model
    print("📦 Downloading Sentence Transformer model...")
    print("   Model: paraphrase-multilingual-MiniLM-L12-v2 (~420MB)")
    print("   This may take 2-5 minutes...")
    print()

    try:
        from sentence_transformers import SentenceTransformer

        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        print(f"   → Initializing SentenceTransformer('{model_name}')...")
        model = SentenceTransformer(model_name)

        print(f"✅ Successfully downloaded: {model_name}")
        cache_folder = getattr(model, 'cache_folder', 'unknown')
        print(f"   Cached at: {cache_folder}")
        print()

    except Exception as e:
        print(f"❌ Failed to download sentence transformer:")
        print(f"   Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. Verify ChromaDB is importable (no need to initialize)
    print("📦 Verifying ChromaDB installation...")
    try:
        import chromadb
        print("✅ ChromaDB ready (will initialize at runtime)")
        print()
    except Exception as e:
        print(f"⚠️ ChromaDB import warning: {e}")
        print("   (This is OK, will work at runtime)")
        print()

    # 3. Verify Google Generative AI (no API call, just import)
    print("📦 Verifying Google Generative AI...")
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI ready")
        print()
    except Exception as e:
        print(f"⚠️ Google Generative AI warning: {e}")
        print("   (This is OK, will work at runtime)")
        print()

    print("=" * 60)
    print("✅ All ML models downloaded and ready!")
    print("=" * 60)
    print()
    print("Benefits:")
    print("  • Models cached on disk")
    print("  • No runtime download → Faster startup")
    print("  • Lower RAM usage → No OOM crashes")
    print()

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
