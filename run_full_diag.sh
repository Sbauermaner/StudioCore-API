diff --git a/run_full_diag.sh b/run_full_diag.sh
new file mode 100755
index 0000000000000000000000000000000000000000..6b855927206e17ef52e84f60407c3e840a512911
--- /dev/null
+++ b/run_full_diag.sh
@@ -0,0 +1,6 @@
+#!/usr/bin/env bash
+set -e
+
+echo ">>> Running StudioCore FULL diagnostics..."
+python3 main/full_system_diagnostics.py
+echo ">>> Diagnostics complete (written to main/lgp.txt)"
