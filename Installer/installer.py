from win32api import GetMonitorInfo, MonitorFromPoint
from win32com.client import Dispatch
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime
from elevate import elevate
import ttkbootstrap as ttk
import winreg as reg
import winshell
import sqlite3
import shutil
import sys
import os

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
        progress_label_2.configure(text="Preparing installation ...")
        win.update_idletasks()
        total_items = sum([len(files) for _, _, files in os.walk(source_dir)])
        total_items += sum([1 for _, dirs, _ in os.walk(source_dir) for _ in dirs])
        counter = 0
        progress_label_2.configure(text="Extracting files to installation directory ...")
        win.update_idletasks()
        install_dir = os.path.join(directory_entry.get(), "SongVibe")
        if os.path.exists(install_dir): shutil.rmtree(install_dir)
        os.makedirs(install_dir)
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(install_dir, item)
            if os.path.isdir(s): shutil.copytree(s, d, dirs_exist_ok=True)
            else: shutil.copy2(s, d)
            counter += 1
            progress_bar['value'] = (counter / total_items) * 90
            win.update_idletasks()
        progress_label_2.configure(text="Creating App Data folders ...")
        win.update_idletasks()
        appdata_dir = os.path.join(os.environ.get("LOCALAPPDATA"), "SongVibe")
        if os.path.exists(appdata_dir): shutil.rmtree(appdata_dir)
        os.makedirs(appdata_dir)
        os.makedirs(os.path.join(appdata_dir, "data"))
        os.makedirs(os.path.join(appdata_dir, "music"))
        os.makedirs(os.path.join(appdata_dir, "temp"))
        progress_bar['value'] = 92
        win.update_idletasks()
        progress_label_2.configure(text="Saving installation information ...")
        win.update_idletasks()
        os.makedirs(os.path.join(install_dir, "resources/data"))
        conn = sqlite3.connect(os.path.join(install_dir, "resources/data/installation.db"))
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS installation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                install_dir TEXT,
                appdata_dir TEXT,
                dateModified TEXT
        )""")
        cursor.execute("INSERT INTO installation (install_dir, appdata_dir, dateModified) VALUES (?, ?, ?)", (install_dir, appdata_dir, str(datetime.now())[0:19]))
        conn.commit()
        conn.close()
        progress_bar['value'] = 94
        win.update_idletasks()
        if checkbox_1_var.get() == 1:
            try:
                progress_label_2.configure(text="Pinning to Start Menu ...")
                win.update_idletasks()
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortcut(os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs", "SongVibe.lnk"))
                shortcut.TargetPath = os.path.join(install_dir, "SongVibe.exe")
                shortcut.WorkingDirectory = os.path.dirname(os.path.join(install_dir, "SongVibe.exe"))
                shortcut.IconLocation = os.path.join(install_dir, "SongVibe.exe")
                shortcut.save()
            except: messagebox.showerror("ERROR", "An error occurred while trying to pin SongVibe to the Start Menu")
        progress_bar['value'] = 96
        win.update_idletasks()
        if checkbox_2_var.get() == 1:
            try:
                progress_label_2.configure(text="Creating Desktop Shortcut ...")
                win.update_idletasks()
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortcut(os.path.join(winshell.desktop(), "SongVibe.lnk"))
                shortcut.TargetPath = os.path.join(install_dir, "SongVibe.exe")
                shortcut.WorkingDirectory = os.path.dirname(os.path.join(install_dir, "SongVibe.exe"))
                shortcut.IconLocation = os.path.join(install_dir, "SongVibe.exe")
                shortcut.save()
            except: messagebox.showerror("ERROR", "An error occurred while trying to create a Desktop Shortcut")
        progress_bar['value'] = 98
        win.update_idletasks()
        progress_label_2.configure(text="Registering SongVibe into Windows applications list ...")
        win.update_idletasks()
        uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        uninstall_string = f'"{os.path.join(install_dir, "Uninstall.exe")}"'
        reg_key = reg.CreateKey(reg.HKEY_LOCAL_MACHINE, os.path.join(uninstall_key, "SongVibe"))
        reg.SetValueEx(reg_key, "DisplayName", 0, reg.REG_SZ, "SongVibe")
        reg.SetValueEx(reg_key, "DisplayVersion", 0, reg.REG_SZ, "1.0.0")
        reg.SetValueEx(reg_key, "Publisher", 0, reg.REG_SZ, "Luis Alejandro Rey de Castro")
        reg.SetValueEx(reg_key, "InstallLocation", 0, reg.REG_SZ, install_dir)
        reg.SetValueEx(reg_key, "UninstallString", 0, reg.REG_SZ, uninstall_string)
        reg.SetValueEx(reg_key, "DisplayIcon", 0, reg.REG_SZ, os.path.join(install_dir, "SongVibe.exe"))
        reg.SetValueEx(reg_key, "Comments", 0, reg.REG_SZ, "Developed for people who love music, just like I do")
        reg.CloseKey(reg_key)
        progress_bar['value'] = 100
        progress_label_2.configure(text="Installation completed successfully ...")
        win.update_idletasks()
        messagebox.showinfo("SUCCESS", "Installation completed successfully\nI hope you have a great experience using SongVibe")
    except: messagebox.showerror("ERROR", "An error occurred while trying to install SongVibe on your device")
    win.destroy()

source_dir = os.path.join(sys._MEIPASS, 'SongVibe')
elevate(show_console=False)

win = ttk.Window(title="SongVibe Installer", themename="cosmo", iconphoto=os.path.join(source_dir, "resources/img/icon.png"))

style = ttk.Style()
style.configure("TCheckbutton", font=f"-size 11")
style.configure("TButton", font=f"-size 12 -weight bold")

root = ttk.Frame(win, padding=40)
root.pack(fill=BOTH, expand=TRUE)

general_frame = ttk.Frame(root, padding=(0, 0, 0, 20))
general_frame.pack(fill=X, expand=FALSE)
general_label_1 = ttk.Label(general_frame, text="General Information", font=f"-size 12 -weight bold")
general_label_1.pack(anchor=W, pady=(0, 5))
general_label_2 = ttk.Label(general_frame, text="App Name: SongVibe", font=f"-size 12")
general_label_2.pack(anchor=W, pady=5)
general_label_3 = ttk.Label(general_frame, text="App Version: 1.0.0", font=f"-size 12")
general_label_3.pack(anchor=W, pady=5)
general_label_4 = ttk.Label(general_frame, text="Developer: Luis Alejandro Rey de Castro", font=f"-size 12")
general_label_4.pack(anchor=W, pady=5)
general_label_5 = ttk.Label(general_frame, text="Comments: Developed for people who love music, just like I do", font=f"-size 12")
general_label_5.pack(anchor=W, pady=(5, 0))

configuration_frame = ttk.Frame(root, padding=(0, 20, 0, 0))
configuration_frame.pack(fill=X, expand=FALSE)
configuration_label = ttk.Label(configuration_frame, text="Installation Configuration", font=f"-size 12 -weight bold")
configuration_label.pack(anchor=W)

checkboxes_frame = ttk.Frame(root, padding=(0, 20, 0, 10))
checkboxes_frame.pack(fill=X, expand=FALSE)
checkbox_1_var = ttk.IntVar(value=1)
checkbox_1 = ttk.Checkbutton(checkboxes_frame, text="Pin to Start Menu", variable=checkbox_1_var, bootstyle="TCheckbutton", cursor="hand2")
checkbox_1.pack(side=LEFT, padx=(0, 30))
checkbox_2_var = ttk.IntVar(value=1)
checkbox_2 = ttk.Checkbutton(checkboxes_frame, text="Create Desktop Shortcut", variable=checkbox_2_var, bootstyle="TCheckbutton", cursor="hand2")
checkbox_2.pack(side=RIGHT, padx=(30, 0))

directory_frame = ttk.Frame(root, padding=(0, 20, 0, 20))
directory_frame.pack(fill=X, expand=FALSE)
directory_entry = ttk.Entry(directory_frame, font=f"-size 12")
directory_entry.insert(0, os.environ.get("PROGRAMFILES"))
directory_entry.configure(state=READONLY)
directory_entry.pack(side=LEFT, fill=X, expand=TRUE, padx=(0, 20))
directory_button = ttk.Button(directory_frame, text="SELECT", width=7, cursor="hand2", bootstyle=PRIMARY, command=select_directory)
directory_button.pack(side=RIGHT, padx=(20, 0))

progress_frame = ttk.Frame(root, padding=(0, 20, 0, 20))
progress_frame.pack(fill=X, expand=FALSE)
progress_label_1 = ttk.Label(progress_frame, text="Installation Progress", font=f"-size 12 -weight bold")
progress_label_1.pack(anchor=W, pady=(0, 5))
progress_label_2 = ttk.Label(progress_frame, text="Waiting for initialization ...", font=f"-size 12")
progress_label_2.pack(anchor=W, pady=(5, 0))
progress_bar = ttk.Progressbar(progress_frame, bootstyle="SUCCESS-STRIPED", orient=HORIZONTAL, length=100, mode=DETERMINATE)
progress_bar.pack(fill=X, pady=(20, 0))

install_button = ttk.Button(root, text="INSTALL", width=8, cursor="hand2", bootstyle=SUCCESS, command=install)
install_button.pack(pady=(20, 0))

win.update_idletasks()
appX, appY = win.winfo_reqwidth(), win.winfo_reqheight()
monitor_info = GetMonitorInfo(MonitorFromPoint((0,0))).get("Work")
win_spa_x = int((monitor_info[2] - appX) / 2)
win_spa_y = int((monitor_info[3] - appY) / 2)
win.geometry(f'{appX}x{appY}+{win_spa_x}+{win_spa_y}')
win.resizable(0, 0)

win.focus_force()
win.mainloop()