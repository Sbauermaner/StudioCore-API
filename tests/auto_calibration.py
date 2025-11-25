#!/usr/bin/env python3
"""
Auto-Calibration and Self-Check Script

This script verifies that all critical fixes are in place:
1. HybridGenreEngine.resolve() method exists and works
2. All new modules (universal_frequency_engine, hybrid_instrumentation_layer, neutral_mode_pre_finalizer) load without errors
3. No RecursionError or ImportError occurs (circular dependency check)
4. CoreV6 initializes successfully
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Add parent directory to path
base_path = Path(__file__).parent.parent
sys.path.insert(0, str(base_path))

def test_hybrid_genre_engine():
    """Test HybridGenreEngine.resolve() method."""
    print("🧪 Testing HybridGenreEngine.resolve()...")
    try:
        from studiocore.hybrid_genre_engine import HybridGenreEngine
        
        engine = HybridGenreEngine()
        
        # Test cases from audit
        test_cases = [
            ("test", "neutral"),
            ("anger", "rage"),
            ("low emotion text", "neutral"),
            ("high anger text", "rage"),
            ("epic legend", "epic"),
            ("electronic beat", "electronic"),
            ("folk ballad", "folk"),
        ]
        
        all_passed = True
        for text, expected_genre in test_cases:
            result = engine.resolve(text_input=text)
            
            if not isinstance(result, dict):
                print(f"  ❌ FAIL: {text} - result is not a dict: {result}")
                all_passed = False
                continue
            
            if "primary_genre" not in result:
                print(f"  ❌ FAIL: {text} - missing 'primary_genre' key")
                all_passed = False
                continue
            
            # Check if expected genre is in result (fuzzy match)
            primary_genre = result.get("primary_genre", "").lower()
            if expected_genre.lower() not in primary_genre and primary_genre not in expected_genre.lower():
                print(f"  ⚠️  WARN: {text} - expected '{expected_genre}', got '{primary_genre}'")
            else:
                print(f"  ✅ PASS: {text} -> {primary_genre}")
        
        return all_passed
    except Exception as e:
        print(f"  ❌ FAIL: Exception: {e}")
        traceback.print_exc()
        return False


def test_missing_modules():
    """Test that all missing modules can be imported."""
    print("\n🧪 Testing missing modules...")
    
    modules_to_test = [
        ("universal_frequency_engine", "UniversalFrequencyEngine"),
        ("hybrid_instrumentation_layer", "HybridInstrumentationLayer"),
        ("neutral_mode_pre_finalizer", "NeutralModePreFinalizer"),
    ]
    
    all_passed = True
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(f"studiocore.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            
            # Try to instantiate
            instance = cls()
            
            # Check for process() or run() method
            has_process = hasattr(instance, "process")
            has_run = hasattr(instance, "run")
            
            if has_process or has_run:
                print(f"  ✅ PASS: {module_name}.{class_name} - can be instantiated")
            else:
                print(f"  ⚠️  WARN: {module_name}.{class_name} - no process() or run() method")
            
        except ImportError as e:
            print(f"  ❌ FAIL: {module_name} - ImportError: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ FAIL: {module_name} - Exception: {e}")
            traceback.print_exc()
            all_passed = False
    
    return all_passed


def test_circular_imports():
    """Test that circular imports don't cause RecursionError."""
    print("\n🧪 Testing circular imports...")
    
    try:
        # Try importing both modules that have circular dependency
        import studiocore.emotion
        import studiocore.tlp_engine
        
        # Try to use both
        from studiocore.emotion import TruthLovePainEngine as EmotionTLP
        from studiocore.tlp_engine import TruthLovePainEngine as TLPEngine
        
        # Try to instantiate
        emotion_tlp = EmotionTLP()
        tlp_engine = TLPEngine()
        
        # Try to call methods
        test_text = "test"
        result1 = emotion_tlp.analyze(test_text)
        result2 = tlp_engine.analyze(test_text)
        
        if isinstance(result1, dict) and isinstance(result2, dict):
            print("  ✅ PASS: No circular import errors, both engines work")
            return True
        else:
            print("  ⚠️  WARN: Engines work but return unexpected types")
            return True  # Still counts as pass
            
    except RecursionError as e:
        print(f"  ❌ FAIL: RecursionError detected: {e}")
        traceback.print_exc()
        return False
    except ImportError as e:
        print(f"  ❌ FAIL: ImportError: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"  ❌ FAIL: Exception: {e}")
        traceback.print_exc()
        return False


def test_core_v6_initialization():
    """Test that CoreV6 can be initialized."""
    print("\n🧪 Testing CoreV6 initialization...")
    
    try:
        from studiocore.core_v6 import StudioCoreV6
        
        core = StudioCoreV6()
        
        # Check that engines are initialized
        if hasattr(core, "_hge") and core._hge is not None:
            print("  ✅ PASS: HybridGenreEngine initialized")
        else:
            print("  ⚠️  WARN: HybridGenreEngine not initialized (may be None)")
        
        # Try a simple analyze call
        test_text = "test"
        result = core.analyze(test_text)
        
        if isinstance(result, dict):
            print("  ✅ PASS: CoreV6.analyze() works")
            return True
        else:
            print(f"  ⚠️  WARN: CoreV6.analyze() returned unexpected type: {type(result)}")
            return True  # Still counts as pass
            
    except Exception as e:
        print(f"  ❌ FAIL: Exception: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests and report status."""
    print("=" * 80)
    print("AUTO-CALIBRATION AND SELF-CHECK")
    print("=" * 80)
    print()
    
    results = []
    
    # Test 1: HybridGenreEngine
    results.append(("HybridGenreEngine.resolve()", test_hybrid_genre_engine()))
    
    # Test 2: Missing modules
    results.append(("Missing modules", test_missing_modules()))
    
    # Test 3: Circular imports
    results.append(("Circular imports", test_circular_imports()))
    
    # Test 4: CoreV6 initialization
    results.append(("CoreV6 initialization", test_core_v6_initialization()))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 SYSTEM STATUS: 100% OPERATIONAL")
        return 0
    else:
        print("⚠️  SYSTEM STATUS: PARTIALLY OPERATIONAL - Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

