"""Script de Compilación Automatizada para Generar el Ejecutable .exe de WEB TESTER EDU (v1.5.0)."""

import os
import subprocess
import sys


def build_standalone_exe():
    print("=== Compilando WEB TESTER EDU en un ejecutable autónomo (.exe) ===")

    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=WEB_TESTER_EDU_v1.5.0",
        "--clean",
        "main.py",
    ]

    print(f"Ejecutando comando: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n¡Compilación exitosa!")
        print("El ejecutable y sus recursos se encuentran en la carpeta:")
        print(os.path.abspath("dist/WEB_TESTER_EDU_v1.5.0"))
    else:
        print("\nError al compilar la aplicación.")


if __name__ == "__main__":
    build_standalone_exe()