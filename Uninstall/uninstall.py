from tkinter import messagebox
import winreg as reg
import subprocess
import winshell
import sqlite3
import shutil
import sys
import os


try:
    if messagebox.askyesno("SongVibe Uninstaller", "Are you sure you want to uninstall SongVibe?\nYou can export all your songs and playlists from the app before uninstalling"):
        current_file_name = os.path.basename(sys.argv[0])
        folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        if current_file_name == "Uninstall.exe" and os.path.basename(folder_path) == "SongVibe":
            uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, os.path.join(uninstall_key, "SongVibe")) as key:
                directory = os.path.dirname(reg.QueryValueEx(key, "UninstallString")[0].strip('"'))
            conn = sqlite3.connect(os.path.join(directory, "resources/data/installation.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM installation")
            dataObtained = cursor.fetchall()[0]
            conn.commit()
            conn.close()
            install_dir, appdata_dir = dataObtained[1], dataObtained[2]
            if os.path.abspath(install_dir) == os.path.abspath(folder_path):
                reg.DeleteKey(reg.HKEY_LOCAL_MACHINE, os.path.join(uninstall_key, "SongVibe"))
                start_menu_shortcut = os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs", "SongVibe.lnk")
                if os.path.exists(start_menu_shortcut): os.remove(start_menu_shortcut)
                desktop_shortcut = os.path.join(winshell.desktop(), "SongVibe.lnk")
                if os.path.exists(desktop_shortcut): os.remove(desktop_shortcut)
                shutil.rmtree(appdata_dir)
                try: shutil.rmtree(install_dir)
                except: pass
                parent_folder = os.path.dirname(folder_path)
                batch_script = "@echo off\n" + "timeout /t 2 >nul 2>nul\n" + f"powershell -Command \"Start-Process cmd -ArgumentList '/c rd /s /q \\\"{folder_path}\\\"' -Verb runAs\"\n" + "timeout /t 1 >nul\n" + "del \"%~f0\" >nul 2>nul" 
                batch_file = os.path.join(parent_folder, "Uninstall_SongVibe.bat")
                with open(batch_file, "w") as f: f.write(batch_script)
                messagebox.showinfo("SUCCESS", "SongVibe was successfully uninstalled from your device\nThank you for using SongVibe")
                subprocess.Popen(batch_file, shell=True)
            else: messagebox.showerror("ERROR", "The installation directory does not coincide with the current directory")
        else: messagebox.showerror("ERROR", "The names of some files and/or folders don't coincide with default ones, preventing the normal uninstallation process")
except: messagebox.showerror("ERROR", f"An error occurred while trying to uninstall SongVibe")
sys.exit()