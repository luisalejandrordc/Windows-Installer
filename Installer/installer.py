import os
import shutil
import sqlite3
import sys
import winreg as reg
from datetime import datetime, timezone
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from elevate import elevate
from ttkbootstrap.constants import BOTH, END, FALSE, LEFT, RIGHT, TRUE, W, X
from ttkbootstrap.style import ACTIVE, DETERMINATE, PRIMARY, READONLY, SUCCESS
from win32api import GetMonitorInfo, MonitorFromPoint
from win32com.client import Dispatch

APP_NAME = "SongVibe"
APP_VERSION = "2.0.0"
DEVELOPER = "Luis Alejandro Rey de Castro"
COMMENTS = "Developed for people who love music, just like I do"

LABEL_FONT_1 = "-size 12 -weight bold"
LABEL_FONT_2 = "-size 12"
CHECKBUTTON_FONT = "-size 11"
BUTTON_FONT = "-size 12 -weight bold"
ENTRY_FONT = "-size 12"

DT_FMT = "%Y-%m-%d %H:%M:%S"


def select_directory():
    directory = filedialog.askdirectory(title="Select Installation Directory")
    if directory:
        directory_entry.configure(state=ACTIVE)
        directory_entry.delete(0, END)
        directory_entry.insert(0, directory)
        directory_entry.configure(state=READONLY)
        root.focus_set()


def install():
    try:
        # PREPARATION
        progress_label_2.configure(text="Preparing installation ...")
        win.update_idletasks()
        total_items = sum(len(dirs) + len(files) for _, dirs, files in os.walk(app_dir))
        counter = 0
        # INSTALL DIRECTORY
        progress_label_2.configure(text="Copying files to installation directory ...")
        win.update_idletasks()
        install_dir = Path(directory_entry.get()) / APP_NAME
        exe_path = install_dir / f"{APP_NAME}.exe"
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
        os.makedirs(install_dir)
        for item in os.listdir(app_dir):
            s = os.path.join(app_dir, item)
            d = os.path.join(install_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
            counter += 1
            progress_bar["value"] = (counter / total_items) * 90
            win.update_idletasks()
        # APP DATA DIRECTORY
        progress_label_2.configure(text="Creating App Data directory ...")
        win.update_idletasks()
        appdata_dir = Path(os.environ["LOCALAPPDATA"]) / APP_NAME
        if os.path.exists(appdata_dir):
            shutil.rmtree(appdata_dir)
        os.makedirs(appdata_dir)
        os.makedirs(appdata_dir / "data")
        os.makedirs(appdata_dir / "temp")
        progress_bar["value"] = 92
        # INSTALLATION DATA
        progress_label_2.configure(text="Saving installation information ...")
        win.update_idletasks()
        os.makedirs(install_dir / "resources/data")
        conn = sqlite3.connect(install_dir / "resources/data/installation.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS installation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                install_dir TEXT,
                appdata_dir TEXT,
                dateCreated TEXT
        )""")
        cursor.execute(
            "INSERT INTO installation (install_dir, appdata_dir, dateCreated) VALUES (?, ?, ?)",
            (install_dir, appdata_dir, datetime.now(timezone.utc).strftime(DT_FMT)),
        )
        conn.commit()
        conn.close()
        progress_bar["value"] = 94
        win.update_idletasks()
        # START MENU SHORTCUT
        if checkbox_1_var.get() == 1:
            try:
                progress_label_2.configure(text="Pinning to Start Menu ...")
                win.update_idletasks()
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(
                    Path(os.environ["ProgramData"])
                    / "Microsoft"
                    / "Windows"
                    / "Start Menu"
                    / "Programs"
                    / f"{APP_NAME}.lnk"
                )
                shortcut.TargetPath = exe_path
                shortcut.WorkingDirectory = APP_NAME
                shortcut.IconLocation = exe_path
                shortcut.save()
            except Exception:
                messagebox.showerror(
                    "ERROR",
                    f"An error occurred while trying to pin {APP_NAME} to the Start Menu",
                )
        progress_bar["value"] = 96
        win.update_idletasks()
        # DESKTOP SHORTCUT
        if checkbox_2_var.get() == 1:
            try:
                progress_label_2.configure(text="Creating Desktop Shortcut ...")
                win.update_idletasks()
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(
                    Path(os.environ["USERPROFILE"]) / "Desktop" / f"{APP_NAME}.lnk"
                )
                shortcut.TargetPath = exe_path
                shortcut.WorkingDirectory = APP_NAME
                shortcut.IconLocation = exe_path
                shortcut.save()
            except Exception:
                messagebox.showerror(
                    "ERROR",
                    "An error occurred while trying to create the Desktop Shortcut",
                )
        progress_bar["value"] = 98
        # WINDOWS APP REGISTRATION
        progress_label_2.configure(
            text=f"Registering {APP_NAME} into Windows applications list ..."
        )
        win.update_idletasks()
        uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        reg_key_path = str(Path(uninstall_key) / APP_NAME)
        uninstall_string = f'"{install_dir / "Uninstall.exe"}"'
        reg_key = reg.CreateKey(reg.HKEY_LOCAL_MACHINE, reg_key_path)
        reg.SetValueEx(reg_key, "DisplayName", 0, reg.REG_SZ, APP_NAME)
        reg.SetValueEx(reg_key, "DisplayVersion", 0, reg.REG_SZ, APP_VERSION)
        reg.SetValueEx(reg_key, "Publisher", 0, reg.REG_SZ, DEVELOPER)
        reg.SetValueEx(reg_key, "InstallLocation", 0, reg.REG_SZ, install_dir)
        reg.SetValueEx(reg_key, "UninstallString", 0, reg.REG_SZ, uninstall_string)
        reg.SetValueEx(reg_key, "DisplayIcon", 0, reg.REG_SZ, exe_path)
        reg.SetValueEx(reg_key, "Comments", 0, reg.REG_SZ, COMMENTS)
        reg.CloseKey(reg_key)
        progress_bar["value"] = 100
        progress_label_2.configure(text="Installation completed successfully ...")
        win.update_idletasks()
        messagebox.showinfo(
            "SUCCESS",
            f"Installation completed successfully\nI hope you have a great experience using {APP_NAME}",
        )
    except Exception:
        messagebox.showerror(
            "ERROR", "An error occurred while trying to install SongVibe on your device"
        )
    win.destroy()


elevate(show_console=False)

app_dir = Path(sys._MEIPASS) / APP_NAME
icon_path = str(app_dir / "resources/icon/icon.png")

win = ttk.Window(title=f"{APP_NAME} Installer", themename="cosmo", iconphoto=icon_path)

style = ttk.Style()
style.configure("TCheckbutton", font=CHECKBUTTON_FONT)
style.configure("TButton", font=BUTTON_FONT)

root = ttk.Frame(win, padding=40)
root.pack(fill=BOTH, expand=TRUE)


# GENERAL INFORMATION
general_frame = ttk.Frame(root, padding=(0, 0, 0, 20))
general_frame.pack(fill=X, expand=FALSE)
general_label_1 = ttk.Label(
    general_frame, text="General Information", font=LABEL_FONT_1
)
general_label_1.pack(anchor=W, pady=(0, 5))
general_label_2 = ttk.Label(
    general_frame, text=f"App Name: {APP_NAME}", font=LABEL_FONT_2
)
general_label_2.pack(anchor=W, pady=5)
general_label_3 = ttk.Label(
    general_frame, text=f"App Version: {APP_VERSION}", font=LABEL_FONT_2
)
general_label_3.pack(anchor=W, pady=5)
general_label_4 = ttk.Label(
    general_frame, text=f"Developer: {DEVELOPER}", font=LABEL_FONT_2
)
general_label_4.pack(anchor=W, pady=5)
general_label_5 = ttk.Label(
    general_frame, text=f"Comments: {COMMENTS}", font=LABEL_FONT_2
)
general_label_5.pack(anchor=W, pady=(5, 0))

# INSTALLATION CONFIGURATION
configuration_frame = ttk.Frame(root, padding=(0, 20, 0, 0))
configuration_frame.pack(fill=X, expand=FALSE)
configuration_label = ttk.Label(
    configuration_frame, text="Installation Configuration", font=LABEL_FONT_1
)
configuration_label.pack(anchor=W)

checkboxes_frame = ttk.Frame(configuration_frame, padding=(0, 20, 0, 10))
checkboxes_frame.pack(fill=X, expand=FALSE)
checkbox_1_var = ttk.IntVar(value=1)
checkbox_1 = ttk.Checkbutton(
    checkboxes_frame,
    text="Pin to Start Menu",
    variable=checkbox_1_var,
    bootstyle="TCheckbutton",
    cursor="hand2",
)
checkbox_1.pack(side=LEFT, padx=(0, 30))
checkbox_2_var = ttk.IntVar(value=1)
checkbox_2 = ttk.Checkbutton(
    checkboxes_frame,
    text="Create Desktop Shortcut",
    variable=checkbox_2_var,
    bootstyle="TCheckbutton",
    cursor="hand2",
)
checkbox_2.pack(side=RIGHT, padx=(30, 0))

directory_frame = ttk.Frame(configuration_frame, padding=(0, 20, 0, 20))
directory_frame.pack(fill=X, expand=FALSE)
directory_entry = ttk.Entry(directory_frame, font=ENTRY_FONT)
directory_entry.insert(0, str(os.environ.get("PROGRAMFILES")))
directory_entry.configure(state=READONLY)
directory_entry.pack(side=LEFT, fill=X, expand=TRUE, padx=(0, 20))
directory_button = ttk.Button(
    directory_frame,
    text="SELECT",
    width=7,
    cursor="hand2",
    bootstyle=PRIMARY,
    command=select_directory,
)
directory_button.pack(side=RIGHT, padx=(20, 0))

# INSTALLATION PROGRESS
progress_frame = ttk.Frame(root, padding=(0, 20, 0, 20))
progress_frame.pack(fill=X, expand=FALSE)
progress_label_1 = ttk.Label(
    progress_frame, text="Installation Progress", font=LABEL_FONT_1
)
progress_label_1.pack(anchor=W, pady=(0, 5))
progress_label_2 = ttk.Label(
    progress_frame, text="Waiting for initialization ...", font=LABEL_FONT_2
)
progress_label_2.pack(anchor=W, pady=(5, 0))
progress_bar = ttk.Progressbar(
    progress_frame,
    bootstyle="SUCCESS-STRIPED",
    orient="horizontal",
    length=100,
    mode=DETERMINATE,
)
progress_bar.pack(fill=X, pady=(20, 0))

install_button = ttk.Button(
    root, text="INSTALL", width=8, cursor="hand2", bootstyle=SUCCESS, command=install
)
install_button.pack(pady=(20, 0))

# WINDOW GEOMETRY
win.update_idletasks()
win_width = win.winfo_reqwidth()
win_height = win.winfo_reqheight()

monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
working_area = monitor_info.get("Work")
USABLE_WIDTH = working_area[2]
USABLE_HEIGHT = working_area[3]

screen_width = win.winfo_screenwidth()
screen_height = win.winfo_screenheight()
if USABLE_WIDTH is not None and USABLE_HEIGHT is not None:
    scale_x = screen_width / USABLE_WIDTH
    scale_y = screen_height / USABLE_HEIGHT
    if scale_x <= scale_y:
        # Scale X is the correct user's screen scale
        geo_width = int(USABLE_WIDTH * scale_x)
        geo_height = int(USABLE_HEIGHT * scale_x)
    else:
        # Scale Y is the correct user's screen scale
        geo_width = int(USABLE_WIDTH * scale_y)
        geo_height = int(USABLE_HEIGHT * scale_y)
else:
    # Just use total screen width and height
    geo_width = screen_width
    geo_height = screen_height
spa_x = (geo_width - win_width) // 2
spa_y = (geo_height - win_height) // 2
win.geometry(f"{win_width}x{win_height}+{spa_x}+{spa_y}")
win.resizable(False, False)

win.focus_force()
win.mainloop()
