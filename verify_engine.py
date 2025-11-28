import sys
import os

# Ensure we can import studiocore
sys.path.insert(0, os.getcwd())


print("⏳ Loading StudioCore...")
try:
    from studiocore import get_core
    core = get_core()
    print("✅ Core Loaded Successfully")
except Exception as e:
    print(f"❌ Core Load Failed: {e}")
    sys.exit(1)


print("\n⏳ Running Analysis Simulation...")
sample_text = "Verse 1\nHello darkness my old friend\nI've come to talk with you again"

try:
    # Run analysis
    result = core.analyze(sample_text)
    
    # Validate Output
    required_keys = ['emotions', 'bpm', 'key', 'style']
    missing = [k for k in required_keys if k not in result]
    
    if missing:
        print(f"❌ Missing keys in result: {missing}")
        sys.exit(1)
    
    print("✅ Analysis Complete!")
    print(f"   - BPM: {result.get('bpm')}")
    print(f"   - Emotions: {list(result.get('emotions', {}).keys())[:3]}...")
    print(f"   - Genre: {result.get('style', {}).get('genre')}")
    
except Exception as e:
    print(f"❌ Analysis Failed with error: {e}")
    sys.exit(1)
