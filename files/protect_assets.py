import os
import stat
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TARGETS = [
    os.path.join(PROJECT_ROOT, "0NOXTACKORE.ico"),
    os.path.join(PROJECT_ROOT, "files", "0NOXTACKORE"),
]

def get_current_windows_user():
    try:
        return subprocess.check_output(["whoami"], text=True).strip()
    except subprocess.CalledProcessError:
        return None


def protect_all():
    for target in TARGETS:
        if os.path.exists(target):
            try:
                protect(target)
            except Exception:
                pass



def set_readonly(path):
    """Set the file or directory to read-only at the filesystem attribute level."""
    if os.name != "nt":
        raise RuntimeError("This script is intended for Windows only.")

    if os.path.exists(path):
        os.chmod(path, stat.S_IREAD)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    os.chmod(os.path.join(root, name), stat.S_IREAD)


def clear_readonly(path):
    if os.name != "nt":
        raise RuntimeError("This script is intended for Windows only.")

    if os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    os.chmod(os.path.join(root, name), stat.S_IWRITE)


def run_icacls(path, args):
    args = ["icacls", path] + args
    subprocess.run(args, check=True, shell=False)


def protect(path):
    print(f"Protegiendo: {path}")
    set_readonly(path)
    user = get_current_windows_user()
    if user:
        run_icacls(path, ["/deny", f"{user}:(DE,DC)"])
    print(f"Protección aplicada en {path}")


def unprotect(path):
    print(f"Desprotegiendo: {path}")
    clear_readonly(path)
    user = get_current_windows_user()
    if user:
        run_icacls(path, ["/remove:d", user])
    print(f"Protección eliminada en {path}")


def main():
    if os.name != "nt":
        print("Este script solo funciona en Windows.")
        sys.exit(1)

    action = "protect"
    if len(sys.argv) > 1 and sys.argv[1] in {"--undo", "unprotect", "restore"}:
        action = "unprotect"

    for target in TARGETS:
        if not os.path.exists(target):
            print(f"Ruta no encontrada: {target}")
            continue

        try:
            if action == "protect":
                protect(target)
            else:
                unprotect(target)
        except subprocess.CalledProcessError as exc:
            print(f"Error al ejecutar icacls en {target}: {exc}")
        except Exception as exc:
            print(f"Error en {target}: {exc}")

    print("Listo.")


if __name__ == "__main__":
    main()
