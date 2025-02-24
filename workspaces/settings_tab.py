import logging
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from phomod_widgets import (
    PHOMODFrame, PHOMODLabelFrame, PHOMODScrollableFrame,
    PHOMODLabel, PHOMODEntry,
    PHOMODComboBox, PHOMODButton, PHOMODCheckbutton,
)

app_logger = logging.getLogger('FOMODLogger')


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                               Base 🏗️
# ----------------------------------------------------------------------------------------------------------------------
class BaseSettingsSection(PHOMODLabelFrame):
    def __init__(self, parent, controller, title, help_text, **kwargs):
        # Create a title label using the controller's title font
        title_label = PHOMODLabel(parent, text=title, font=controller.fonts["title"], help_text=help_text)
        super().__init__(parent, controller=controller, label_widget=title_label, help_text=help_text, **kwargs)
        self.controller = controller


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                     Theme Settings 🎨
# ----------------------------------------------------------------------------------------------------------------------
class ThemeSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Theme Selection", "Change the application's theme.")
        self.theme_options = controller.theme_manager.get_theme_options()
        self.current_theme = controller.theme_manager.get_theme()
        self.theme_var = tk.StringVar(value="Default")
        self._build()

    def _build(self):
        self.theme_menu = PHOMODComboBox(
            self, textvariable=self.theme_var, values=self.theme_options, state="readonly",
            help_text="Select a theme for the application interface."
        )
        self.theme_menu.pack(fill=tk.X, padx=5, pady=5)
        self.theme_menu.bind("<<ComboboxSelected>>", self.apply_theme)

        self.current_theme_label = PHOMODLabel(
            self, font=self.controller.fonts["italic"],
            text=f"Current Theme: {self.current_theme}",
            help_text="Displays the currently active theme. Click to apply a random one!"
        )
        self.current_theme_label.pack(pady=5)
        self.current_theme_label.bind("<Button-1>", self.apply_random_theme)
        app_logger.info("Theme settings section created.")

    def apply_theme(self, event=None):
        selected_theme = self.theme_var.get()
        applied_theme = self.controller.theme_manager.apply_theme(selected_theme)
        if selected_theme == self.controller.theme_manager.separator:
            self.controller.update_status_bar_text("Please select a valid theme.")
            return
        self.current_theme_label.config(text=f"Current Theme: {applied_theme}")
        self.controller.update_status_bar_text(f"Theme set to {applied_theme}.")
        app_logger.info(f"Theme applied: {applied_theme}")

    def apply_random_theme(self, event=None):
        if not self.theme_options:
            return
        random_theme = random.choice(self.theme_options)
        self.theme_var.set(random_theme)
        self.apply_theme()
        app_logger.info(f"Random theme applied: {random_theme}")


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                    Update Settings 🔄
# ----------------------------------------------------------------------------------------------------------------------

class UpdateSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Update Settings", "Configure automatic update checks.")
        self.auto_update_var = tk.BooleanVar(value=True)
        self._build()

    def _build(self):
        PHOMODCheckbutton(
            self, text="Automatically check for updates", variable=self.auto_update_var,
            help_text="Enable or disable automatic update checks."
        ).pack(anchor="w", padx=5, pady=5)
        PHOMODButton(
            self, text="Check Now", help_text="Manually check for updates.",
            command=self.check_for_updates
        ).pack(padx=5, pady=(5, 10))
        app_logger.info("Update settings section created.")

    def check_for_updates(self):
        self.controller.update_status_bar_text("Checking for updates...")
        app_logger.info("Checking for updates...")
        threading.Timer(2.0, lambda: self.controller.update_status_bar_text("No updates available.")).start()
        app_logger.info("Update check completed.")


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                 UI & Accessibility 🌎
# ----------------------------------------------------------------------------------------------------------------------
class UIAccessibilitySettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "UI & Accessibility", "Customize interface settings.")
        self.language_var = tk.StringVar(value="English")
        self.font_size_var = tk.StringVar(value="Normal")
        self._build()

    def _build(self):
        PHOMODLabel(self, text="Language:", help_text="Select UI language.").pack(anchor="w", padx=5, pady=2)
        self.language_menu = PHOMODComboBox(
            self, textvariable=self.language_var,
            values=["English", "Spanish", "French", "German"],
            state="readonly", help_text="Select the language for the application."
        )
        self.language_menu.pack(fill=tk.X, padx=5, pady=5)
        PHOMODLabel(self, text="Font Size:", help_text="Adjust font size for readability.").pack(anchor="w", padx=5, pady=2)
        self.font_size_menu = PHOMODComboBox(
            self, textvariable=self.font_size_var,
            values=["Small", "Normal", "Large"],
            state="readonly", help_text="Select the font size for the UI."
        )
        self.font_size_menu.pack(fill=tk.X, padx=5, pady=5)
        PHOMODButton(
            self, text="Help Translate", help_text="Assist in translating the app into other languages.",
            command=self.ask_for_translation_help
        ).pack(padx=5, pady=5)
        app_logger.info("UI & Accessibility section created.")

    def ask_for_translation_help(self):
        self.controller.update_status_bar_text("Translation help requested.")
        app_logger.info("Translation help button pressed.")
        messagebox.showinfo("Translation Help", "Please visit our GitHub page to contribute translations.")


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                              File & Data Management 🗄
# ----------------------------------------------------------------------------------------------------------------------

class FileDataSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "File & Data Management", "Manage file paths and directories.")
        self.starting_dir_var = tk.StringVar(value="Not Set")
        self._build()

    def _build(self):
        PHOMODLabel(self, text="Default Starting Directory:", help_text="Set a default working directory.").pack(anchor="w", padx=5, pady=2)
        PHOMODEntry(self, textvariable=self.starting_dir_var, state="readonly").pack(fill=tk.X, padx=5, pady=5)
        PHOMODButton(
            self, text="Set Directory", command=self.choose_starting_directory,
            help_text="Select a default directory."
        ).pack(padx=5, pady=5)
        app_logger.info("File & Data Management section created.")

    def choose_starting_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.starting_dir_var.set(directory)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                   Logging Settings 📜
# ----------------------------------------------------------------------------------------------------------------------
class LoggingSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Logging Settings", "Configure logging preferences.")
        self.disable_logging_var = tk.BooleanVar(value=False)
        self.log_rotation_var = tk.StringVar(value="Daily")
        self.log_path_var = tk.StringVar(value="Not Set")
        self._build()

    def _build(self):
        PHOMODLabel(self, text="Log Rotation:", help_text="Select log rotation frequency.").pack(anchor="w", padx=5, pady=2)
        self.log_rotation_menu = PHOMODComboBox(
            self, textvariable=self.log_rotation_var, values=["Daily", "Weekly", "Max file size"],
            state="readonly", help_text="Select how frequently logs rotate."
        )
        self.log_rotation_menu.pack(fill=tk.X, padx=5, pady=5)
        PHOMODLabel(self, text="Log File Location:", help_text="Choose where logs are stored.").pack(anchor="w", padx=5, pady=2)
        PHOMODEntry(self, textvariable=self.log_path_var, state="readonly").pack(fill=tk.X, padx=5, pady=5)
        PHOMODButton(
            self, text="Set Log Location", command=self.choose_log_location,
            help_text="Select a directory to save logs."
        ).pack(padx=5, pady=5)
        PHOMODCheckbutton(
            self, text="Disable Logging", variable=self.disable_logging_var,
            help_text="Turn off logging entirely."
        ).pack(anchor="w", padx=5, pady=5)
        app_logger.info("Logging Settings section created.")

    def choose_log_location(self):
        directory = filedialog.askdirectory()
        if directory:
            self.log_path_var.set(directory)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                               Tab Control Settings 📂
# ----------------------------------------------------------------------------------------------------------------------
class TabControlSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Tab Control", "Hide or show certain tabs.")
        self.hidden_tabs = {}
        self.required_tabs = {"Project", "Settings"}
        self._build()

    def _build(self):
        tab_check_frame = PHOMODFrame(self)
        tab_check_frame.pack(fill=tk.X, padx=5, pady=5)
        for tab in self.controller.get_available_tabs():
            if tab not in self.required_tabs:
                self.hidden_tabs[tab] = tk.BooleanVar(value=False)
                PHOMODCheckbutton(
                    tab_check_frame, text=f"Hide {tab}", command=self.apply_tab_visibility,
                    variable=self.hidden_tabs[tab], help_text=f"Toggle visibility of the {tab} tab."
                ).pack(anchor="w", padx=5, pady=2)
        app_logger.info("Tab Control section created.")

    def apply_tab_visibility(self):
        for tab, var in self.hidden_tabs.items():
            if var.get():
                self.controller.show_tab(tab)
            else:
                self.controller.hide_tab(tab)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                   Advanced Options 🔧
# ----------------------------------------------------------------------------------------------------------------------
class AdvancedSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Advanced Options", "Enable additional debugging tools.")
        self.developer_mode_var = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        PHOMODCheckbutton(
            self, text="Developer Mode", variable=self.developer_mode_var,
            help_text="Enables additional debugging options."
        ).pack(anchor="w", padx=5, pady=5)
        app_logger.info("Advanced Options section created.")


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                      About Section ℹ️
# ----------------------------------------------------------------------------------------------------------------------
class AboutSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "About", "View information about PHOMOD.")
        self._build()

    def _build(self):
        about_text = (
            "PHOMOD - Mod Organizer\nVersion 1.0\n\n"
            "Developed by Stephanie Burns\n"
            "Visit the GitHub repository for more info!"
        )
        PHOMODLabel(
            self, text=about_text, help_text="Application version and credits.",
            anchor="center", justify="center"
        ).pack(expand=True, padx=5, pady=10)
        app_logger.info("About section created.")


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                               Main 🏠
# ----------------------------------------------------------------------------------------------------------------------
class SettingsTab(PHOMODFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        self.controller = controller
        self._create_scrollable_container()
        self._populate_sections()
        app_logger.info("SettingsTab initialized.")
        self.controller.update_status_bar_text("🛠️ Settings loaded successfully!")

    def _create_scrollable_container(self):
        self.scrollable_frame = PHOMODScrollableFrame(self, controller=self.controller)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)
        self.inner_frame = self.scrollable_frame.inner_frame

    def _populate_sections(self):
        ThemeSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        UpdateSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        UIAccessibilitySettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        FileDataSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        LoggingSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        TabControlSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        AdvancedSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        AboutSection(self.inner_frame, self.controller).pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        # Apply theme after sections are built
        self.after(0, lambda: self.controller.theme_manager.apply_theme(self.controller.theme_manager.get_theme()))
