#!/usr/bin/env python3
"""
Validation script to check if the setup is correct and API key is working
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.11+")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking .env file...")
    env_path = Path(".env")

    if not env_path.exists():
        print("❌ .env file not found!")
        print("   Run: cp .env.example .env")
        return False

    print("✅ .env file exists")

    # Read and check variables
    required_vars = ["LLM_PROVIDER", "LLM_API_KEY", "LLM_MODEL", "EMBEDDINGS_MODEL"]
    env_vars = {}

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value

    missing = []
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing.append(var)
        elif var == "LLM_API_KEY" and env_vars[var] in ["your-api-key-here", ""]:
            print(f"⚠️  {var} is not set (still has placeholder value)")
            return False

    if missing:
        print(f"❌ Missing variables: {', '.join(missing)}")
        return False

    print(f"✅ All required variables present")
    print(f"   Provider: {env_vars.get('LLM_PROVIDER')}")
    print(f"   Model: {env_vars.get('LLM_MODEL')}")
    print(f"   Embeddings: {env_vars.get('EMBEDDINGS_MODEL')}")

    # Mask API key for security
    api_key = env_vars.get('LLM_API_KEY', '')
    if api_key:
        masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
        print(f"   API Key: {masked}")

    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")

    required_packages = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "pandas",
        "PyPDF2",
        "docx",
        "openai",
        "google.generativeai",
        "chromadb",
        "pydantic",
        "pytest"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False

    print(f"✅ All {len(required_packages)} required packages installed")
    return True

def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Checking directories...")

    required_dirs = [
        "backend/app",
        "backend/app/api",
        "backend/app/core",
        "backend/app/agents",
        "backend/app/utils",
        "ui",
        "tests",
        "docs"
    ]

    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)

    if missing:
        print(f"❌ Missing directories: {', '.join(missing)}")
        return False

    print(f"✅ All {len(required_dirs)} required directories exist")

    # Create data directories if they don't exist
    data_dirs = ["data/chroma", "temp_uploads"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created data directories: {', '.join(data_dirs)}")

    return True

def test_api_key():
    """Test if API key is valid by making a simple request"""
    print("\n🔍 Testing API key...")

    try:
        from backend.app.config import settings

        if settings.llm_provider.lower() == "openai":
            print("   Testing OpenAI API key...")
            import openai
            client = openai.OpenAI(api_key=settings.llm_api_key)

            # Simple test: list models or create a minimal completion
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                print("✅ OpenAI API key is valid and working!")
                return True
            except openai.AuthenticationError:
                print("❌ OpenAI API key is invalid!")
                print("   Check your key at: https://platform.openai.com/api-keys")
                return False
            except openai.RateLimitError:
                print("⚠️  OpenAI API key valid but rate limited")
                print("   Check your usage at: https://platform.openai.com/usage")
                return True
            except Exception as e:
                print(f"⚠️  OpenAI API error: {str(e)}")
                return False

        elif settings.llm_provider.lower() == "gemini":
            print("   Testing Gemini API key...")
            import google.generativeai as genai

            try:
                genai.configure(api_key=settings.llm_api_key)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Hi", generation_config={"max_output_tokens": 5})
                print("✅ Gemini API key is valid and working!")
                return True
            except Exception as e:
                print(f"❌ Gemini API error: {str(e)}")
                print("   Check your key at: https://makersuite.google.com/app/apikey")
                return False
        else:
            print(f"⚠️  Unknown provider: {settings.llm_provider}")
            return False

    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
        return False

def check_config_imports():
    """Check if config is properly imported in all modules"""
    print("\n🔍 Checking config imports...")

    try:
        from backend.app.config import settings
        from backend.app.core.embeddings import EmbeddingsProvider, LLMProvider
        from backend.app.core.vector_store import VectorStore

        print("✅ All config imports working")
        print(f"   Settings loaded: Provider={settings.llm_provider}, Model={settings.llm_model}")
        return True
    except Exception as e:
        print(f"❌ Config import error: {str(e)}")
        return False

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("GenAI Document Assistant - Setup Validation")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Config Imports", check_config_imports),
        ("API Key", test_api_key),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! You're ready to run the application.")
        print("\nNext steps:")
        print("  1. Start API:  python -m uvicorn backend.app.main:app --reload")
        print("  2. Start UI:   streamlit run ui/streamlit_app.py")
        print("  3. Open UI:    http://localhost:8501")
    else:
        print("⚠️  SOME CHECKS FAILED. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Missing .env: cp .env.example .env (then edit with your API key)")
        print("  - Missing deps: pip install -r requirements.txt")
        print("  - Invalid API key: Check at https://platform.openai.com/api-keys")
    print("=" * 60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
