import os
import shutil
import subprocess
import sys
import winreg as reg
from pathlib import Path
from tkinter import messagebox

APP_NAME = "SongVibe"

file_path = Path(sys.argv[0]).resolve()
dir_path = file_path.parent

if file_path.name == "Uninstall.exe" and dir_path.name == APP_NAME:
    try:
        uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        reg_key_path = str(Path(uninstall_key) / APP_NAME)
        with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, reg_key_path) as key:
            uninstall_str = reg.QueryValueEx(key, "UninstallString")[0].strip('"')
            uninstall_dir = Path(uninstall_str).parent
        if dir_path == uninstall_dir:
            if messagebox.askyesno(
                f"{APP_NAME} Uninstaller",
                f"Are you sure you want to uninstall {APP_NAME}?\nYou can export all your playlists and songs from the app before uninstalling it",
            ):
                # REGISTER KEY
                reg.DeleteKey(reg.HKEY_LOCAL_MACHINE, reg_key_path)
                # START MENU SHORTCUT
                start_menu_shortcut = (
                    Path(os.environ["ProgramData"])
                    / "Microsoft"
                    / "Windows"
                    / "Start Menu"
                    / "Programs"
                    / f"{APP_NAME}.lnk"
                )
                start_menu_shortcut.unlink(missing_ok=True)
                # DESKTOP SHORTCUT
                desktop_shortcut = (
                    Path(os.environ["USERPROFILE"]) / "Desktop" / f"{APP_NAME}.lnk"
                )
                desktop_shortcut.unlink(missing_ok=True)
                # APPDATA DIRECTORY
                shutil.rmtree(Path(os.environ["LOCALAPPDATA"]) / APP_NAME)
                try:
                    shutil.rmtree(dir_path)
                except Exception:
                    pass
                batch_script = (
                    "@echo off\n"
                    + "timeout /t 2 >nul 2>nul\n"
                    + f'powershell -Command "Start-Process cmd -ArgumentList \'/c rd /s /q \\"{str(dir_path)}\\"\' -Verb runAs"\n'
                    + "timeout /t 1 >nul\n"
                    + 'del "%~f0" >nul 2>nul'
                )
                batch_file = dir_path.parent / f"Uninstall_{APP_NAME}.bat"
                with open(batch_file, "w") as f:
                    f.write(batch_script)
                messagebox.showinfo(
                    "SUCCESS",
                    f"{APP_NAME} was successfully uninstalled from your device\nThank you for using {APP_NAME}",
                )
                subprocess.Popen(batch_file, shell=True)
        else:
            messagebox.showerror(
                "ERROR",
                "The installation directory does not coincide with the current directory",
            )
    except Exception:
        messagebox.showerror(
            "ERROR", f"An error occurred while trying to uninstall {APP_NAME}"
        )
else:
    messagebox.showerror(
        "ERROR",
        "The name of some files or directories don't coincide with default ones, preventing the normal uninstallation process",
    )
sys.exit()
