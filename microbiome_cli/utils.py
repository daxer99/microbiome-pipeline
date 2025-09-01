import subprocess
import os
from datetime import datetime


def run_cmd(cmd, cwd=None):
    """Ejecuta un comando shell y muestra salida en tiempo real."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    if result.stdout.strip():
        print(result.stdout.strip())
    return result