diff --git a/main/auto_trigger.py b/main/auto_trigger.py
new file mode 100644
index 0000000000000000000000000000000000000000..e384f52f87aa2937a13bc3781bba0bde7a7b4dd4
--- /dev/null
+++ b/main/auto_trigger.py
@@ -0,0 +1,6 @@
+# Auto-trigger for full diagnostics — created 2025-11-21T22:04:15.340308 UTC
+import subprocess
+import sys
+print(">>> AutoTrigger: launching full diagnostics...")
+subprocess.run(["bash", "../run_full_diag.sh"], check=True)
+print(">>> AutoTrigger complete")
