# -*- coding: utf-8 -*-
"""
🔍 StudioCore Compatibility Audit (Full)
Author: Bauer Synesthetic Studio
"""
from compat_check_core import run_check as core_check
from compat_check_remote import run_check as remote_check

if __name__ == "__main__":
    print("=== 🔍 StudioCore Compatibility Audit ===\n")
    core_check()
    print("\n---\n")
    remote_check()
    print("\n✅ Audit complete.")
