import sys
import subprocess
import os


def install_flake8():
    try:
        import flake8  # noqa: F401
    except ImportError:
        print("Install flake8 check tool...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flake8"])


def run_audit():
    install_flake8()

    output_file = "errors_report.txt"
    print(f"\n--- Start checking code in: {os.getcwd()} ---")

    # Параметры запуска:
    # --exclude: пропускаем системные папки
    # --ignore=E501: не ругаться на длинные строки (самая частая и бесполезная ошибка)
    # . : проверяем текущую папку
    cmd = [
        sys.executable,
        "-m",
        "flake8",
        ".",
        f"--output-file={output_file}",
        "--exclude=.git,__pycache__,venv,env,node_modules,build,dist",
        "--ignore=E501,W503",
    ]

    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error starting flake8: {e}")
        return

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        count = len(lines)
        print(f"--- DONE. Found potential issues: {count} ---")
        print(f"Full report saved to: {output_file}")

        if count > 0:
            print("\nExample of first 5 errors:")
            print("".join(lines[:5]))
            print("...")
    else:
        print("Report file was not created. (Maybe no errors found or access denied)")


if __name__ == "__main__":
    run_audit()
