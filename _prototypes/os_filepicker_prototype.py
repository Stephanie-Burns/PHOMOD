
import os
import platform
import subprocess
from tkinter import filedialog


class FilePicker:
    """Unified file and folder picker with native OS dialogs and Tkinter fallback."""

    FILTERS = {
        "all": [("All Files", "*.*")],
        "images": [("Image Files", "*.png *.PNG *.jpg *.JPG *.jpeg *.JPEG *.bmp *.BMP *.gif *.GIF")],
        "text": [("Text Files", "*.txt *.TXT")],
        "scripts": [("Python Scripts", "*.py"), ("Shell Scripts", "*.sh"), ("Batch Files", "*.bat")],
        "archives": [("Archives", "*.zip;*.tar.gz;*.7z;*.rar")],
        "documents": [("Documents", "*.pdf *.PDF *.docx *.DOCX *.odt *.ODT")],
    }

    @staticmethod
    def _run_command(command):
        """Helper function to execute a command silently and return its output, or None if it fails."""
        try:
            return subprocess.check_output(command, universal_newlines=True, stderr=subprocess.DEVNULL).strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            return None  # Silently fail and return None

    @staticmethod
    def select_folder():
        """Opens the system's native folder picker or falls back to Tkinter."""
        system = platform.system()
        selected_folder = None

        if system == "Linux":
            selected_folder = FilePicker._run_command(["kdialog", "--getexistingdirectory", os.getcwd()])
            if not selected_folder:
                selected_folder = FilePicker._run_command(["zenity", "--file-selection", "--directory"])
            if not selected_folder:
                selected_folder = FilePicker._run_command(["xdg-user-dir", "DOCUMENTS"])  # Default to Documents

        elif system == "Windows":
            selected_folder = FilePicker._run_command([
                "powershell", "-Command",
                "(New-Object -ComObject Shell.Application).BrowseForFolder(0, 'Select Folder', 0).Self.Path"
            ])

        elif system == "Darwin":  # macOS
            selected_folder = FilePicker._run_command([
                "osascript", "-e",
                'tell application "Finder" to return POSIX path of (choose folder with prompt "Select Folder")'
            ])

        if not selected_folder or not os.path.isdir(selected_folder):
            selected_folder = filedialog.askdirectory()

        return selected_folder if os.path.isdir(selected_folder) else None

    @staticmethod
    def select_file(filetypes=("Image Files", "*.png *.PNG *.jpg *.JPG *.jpeg *.JPEG *.bmp *.BMP *.gif *.GIF")):
        """Opens the system's native file picker or falls back to Tkinter."""
        system = platform.system()
        selected_file = None

        if system == "Linux":
            selected_file = FilePicker._run_command(["kdialog", "--getopenfilename"])
            if not selected_file:
                selected_file = FilePicker._run_command(["zenity", "--file-selection"])

        elif system == "Windows":
            selected_file = FilePicker._run_command([
                "powershell", "-Command",
                "[System.Windows.Forms.OpenFileDialog]::new().ShowDialog() | Out-Null; [System.Windows.Forms.OpenFileDialog]::new().FileName"
            ])

        elif system == "Darwin":  # macOS
            selected_file = FilePicker._run_command([
                "osascript", "-e",
                'POSIX path of (choose file with prompt "Select a file")'
            ])

        if not selected_file or not os.path.isfile(selected_file):
            selected_file = filedialog.askopenfilename(filetypes=filetypes)

        return selected_file if os.path.isfile(selected_file) else None


# class somewidget:
#     def select_folder(self):
#         """Opens the system's native file picker if possible, otherwise falls back to Tkinter's."""
#         selected_folder = None
#         system = platform.system()
#
#         def run_command(command):
#             """Helper function to run a command silently and return output or None."""
#             try:
#                 return subprocess.check_output(command, universal_newlines=True, stderr=subprocess.DEVNULL).strip()
#             except (FileNotFoundError, subprocess.CalledProcessError):
#                 return None  # Silently fail and return None
#
#         if system == "Linux":
#             # Try KDE's kdialog first, then Zenity (GNOME), then xdg-desktop-portal
#             selected_folder = run_command(["kdialog", "--getexistingdirectory", os.getcwd()])
#             if not selected_folder:
#                 selected_folder = run_command(["zenity", "--file-selection", "--directory"])
#             if not selected_folder:
#                 selected_folder = run_command(
#                     ["xdg-user-dir", "DOCUMENTS"])  # Last resort, get default documents folder
#
#         elif system == "Windows":
#             # Use native Explorer dialog
#             selected_folder = run_command([
#                 "powershell", "-Command",
#                 "(New-Object -ComObject Shell.Application).BrowseForFolder(0, 'Select Folder', 0).Self.Path"
#             ])
#
#         elif system == "Darwin":  # macOS
#             selected_folder = run_command([
#                 "osascript", "-e",
#                 'tell application "Finder" to return POSIX path of (choose folder with prompt "Select Folder")'
#             ])
#
#         # If all methods fail, fall back to Tkinter's file picker
#         if not selected_folder or not os.path.isdir(selected_folder):
#             selected_folder = filedialog.askdirectory()
#
#         # Update entry field if a folder was selected
#         if selected_folder and os.path.isdir(selected_folder):
#             self.project_entry.delete(0, tk.END)
#             self.project_entry.insert(0, selected_folder)
#
#     def load_recent_project(self, event):
#         selected_index = self.recent_projects.curselection()
#         if selected_index:
#             selected_path = self.recent_projects.get(selected_index)
#             self.project_entry.delete(0, tk.END)
#             self.project_entry.insert(0, selected_path)
#
#     def on_tree_select(self, event):
#         selected = self.tree.selection()
#         self.controller.toggle_details_tab(enable=bool(selected))
