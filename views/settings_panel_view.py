import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from config import SETTINGS
from phomod_widgets import (
    PHOMODFrame, PHOMODLabelFrame, PHOMODScrollableFrame,
    PHOMODLabel, PHOMODEntry,
    PHOMODComboBox, PHOMODButton, PHOMODCheckbutton,
)

app_logger = logging.getLogger('PHOMODLogger')


# ----------------------------------------------------------------------------------------------------------------------
#                                               Base Settings Section 🏗️
# ----------------------------------------------------------------------------------------------------------------------
class BaseSettingsSection(PHOMODLabelFrame):
    def __init__(self, parent, controller, title, help_text, **kwargs):
        # Attempt to retrieve fonts from controller or its UI; fallback to defaults.
        fonts = None
        if hasattr(controller, "fonts"):
            fonts = controller.fonts
        elif hasattr(controller, "ui") and hasattr(controller.ui, "fonts"):
            fonts = controller.ui.fonts
        if fonts is None:
            fonts = {
                "title": ("Helvetica", 12, "bold"),
                "italic": ("Helvetica", 10, "italic")
            }
        title_label = PHOMODLabel(
            parent, text=title, font=fonts["title"], help_text=help_text
        )
        super().__init__(parent, controller=controller, label_widget=title_label, help_text=help_text, **kwargs)
        self.controller = controller
        self.fonts = fonts  # Save fonts for later use in child sections


# ----------------------------------------------------------------------------------------------------------------------
#                                           Theme Settings Section 🎨
# ----------------------------------------------------------------------------------------------------------------------
class ThemeSettingsSection(BaseSettingsSection):
    """Settings section for selecting and applying themes."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Theme Selection", "Change the application's theme.")
        self.theme_manager = controller.theme_manager
        # Use the current theme from the theme manager (assumed already capitalized)
        self.theme_var = tk.StringVar(value=self.theme_manager.get_theme())
        self._build()

    def _build(self):
        self.theme_menu = PHOMODComboBox(
            self,
            textvariable=self.theme_var,
            values=self.theme_manager.get_themes(),
            state="readonly",
            help_text="Select a theme for the application interface."
        )
        self.theme_menu.pack(fill=tk.X, padx=5, pady=5)
        self.theme_menu.bind("<<ComboboxSelected>>", self.apply_theme)

        self.current_theme_label = PHOMODLabel(
            self,
            font=self.fonts["italic"],
            text=self.theme_var.get(),
            textvariable=self.theme_var,
            help_text="Displays the currently active theme. Click to apply a random one!"
        )
        self.current_theme_label.pack(pady=5)
        self.current_theme_label.bind("<Button-1>", self.apply_smart_random_theme)

        app_logger.debug("🏗️ Theme settings UI initialized.")

    def apply_theme(self, event=None):
        """Apply the selected theme and update the UI."""
        selected_theme = self.theme_var.get()
        applied_theme = self.theme_manager.apply_theme(selected_theme)
        if applied_theme:
            self.theme_var.set(applied_theme)
            self.controller.update_status_bar_text(f"Theme set to {applied_theme}.")
            app_logger.debug(f"🎨 Theme applied: {applied_theme}")

    def apply_smart_random_theme(self, event=None):
        """Apply a smart random theme (avoiding immediate repetition)."""
        random_theme = self.theme_manager.get_smart_random_theme()
        if random_theme:
            self.theme_var.set(random_theme)
            self.apply_theme()


# ----------------------------------------------------------------------------------------------------------------------
#                                          Update Settings Section 🔄
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

        app_logger.info("🏗️ Update settings section created.")

    def check_for_updates(self):
        self.controller.update_status_bar_text("Checking for updates...")
        app_logger.info("Checking for updates...")
        threading.Timer(2.0, lambda: self.controller.update_status_bar_text("No updates available.")).start()
        app_logger.info("Update check completed.")


# ----------------------------------------------------------------------------------------------------------------------
#                                     UI & Accessibility Settings Section 🌎
# ----------------------------------------------------------------------------------------------------------------------
class UIAccessibilitySettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "UI & Accessibility", "Customize interface settings.")
        self.language_var = tk.StringVar(value="English")
        self.font_size_var = tk.StringVar(value="Normal")
        self._build()

    def _build(self):
        PHOMODLabel(
            self, text="Language:", help_text="Select UI language."
        ).pack(anchor="w", padx=5, pady=2)

        self.language_menu = PHOMODComboBox(
            self, textvariable=self.language_var,
            values=["English", "Spanish", "French", "German"],
            state="readonly", help_text="Select the language for the application."
        )
        self.language_menu.pack(fill=tk.X, padx=5, pady=5)

        PHOMODLabel(
            self, text="Font Size:", help_text="Adjust font size for readability."
        ).pack(anchor="w", padx=5, pady=2)

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

        app_logger.info("🏗️ UI & Accessibility section created.")

    def ask_for_translation_help(self):
        self.controller.update_status_bar_text("Translation help requested.")
        app_logger.info("Translation help button pressed.")
        messagebox.showinfo("Translation Help", "Please visit our GitHub page to contribute translations.")


# ----------------------------------------------------------------------------------------------------------------------
#                                    File & Data Management Settings Section 🗄
# ----------------------------------------------------------------------------------------------------------------------
class FileDataSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "File & Data Management", "Manage file paths and directories.")
        self.starting_dir_var = tk.StringVar(value="Not Set")
        self._build()

    def _build(self):
        PHOMODLabel(
            self, text="Default Starting Directory:", help_text="Set a default working directory."
        ).pack(anchor="w", padx=5, pady=2)

        PHOMODEntry(
            self, textvariable=self.starting_dir_var, state="readonly"
        ).pack(fill=tk.X, padx=5, pady=5)

        PHOMODButton(
            self, text="Set Directory", command=self.choose_starting_directory,
            help_text="Select a default directory."
        ).pack(padx=5, pady=5)

        app_logger.info("🏗️ File & Data Management section created.")

    def choose_starting_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.starting_dir_var.set(directory)


# ----------------------------------------------------------------------------------------------------------------------
#                                     Logging Settings Section 📜
# ----------------------------------------------------------------------------------------------------------------------
class LoggingSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Logging Settings", "Configure logging preferences.")
        self.disable_logging_var = tk.BooleanVar(value=SETTINGS.get("disable_file_logging", False))
        self.log_rotation_var = tk.StringVar(value=SETTINGS.get("log_rotation", "Max file size"))
        self.log_path_var = tk.StringVar(value=SETTINGS.get("logs_dir", "Not Set"))
        self.log_file_size_var = tk.IntVar(value=SETTINGS.get("max_log_size_mb", 37))
        self.log_level_var = tk.StringVar(value=SETTINGS.get("log_level", "INFO"))
        self._build()

    def _build(self):
        PHOMODLabel(self, text="Log Level:", help_text="Set the verbosity of logging output.").pack(anchor="w", padx=5, pady=2)
        self.log_level_menu = PHOMODComboBox(
            self,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            state="readonly",
            help_text="Select the log level."
        )
        self.log_level_menu.pack(fill=tk.X, padx=5, pady=5)
        self.log_level_menu.bind("<<ComboboxSelected>>", self.on_log_level_change)

        PHOMODLabel(self, text="Log Rotation:", help_text="Select log rotation frequency.").pack(anchor="w", padx=5, pady=2)
        self.log_rotation_menu = PHOMODComboBox(
            self,
            textvariable=self.log_rotation_var,
            values=["Max file size", "Monthly", "Weekly"],
            state="readonly",
            help_text="Select how frequently logs rotate."
        )
        self.log_rotation_menu.pack(fill=tk.X, padx=5, pady=5)
        self.log_rotation_menu.bind("<<ComboboxSelected>>", self.on_log_rotation_change)

        self.log_file_size_frame = PHOMODFrame(self)
        PHOMODLabel(self.log_file_size_frame, text="Max File Size (MB):").pack(side="left", padx=(5, 2))
        self.log_file_size_entry = PHOMODEntry(
            self.log_file_size_frame,
            textvariable=self.log_file_size_var,
            width=6
        )
        self.log_file_size_entry.pack(side="left", padx=5)
        self.log_file_size_entry.bind("<FocusOut>", self.on_log_file_size_change)
        self.log_file_size_frame.pack(anchor="w", padx=5, pady=5)

        PHOMODLabel(self, text="Log File Location:", help_text="Choose where logs are stored.").pack(anchor="w", padx=5, pady=2)
        self.log_path_entry = PHOMODEntry(self, textvariable=self.log_path_var, state="readonly")
        self.log_path_entry.pack(fill=tk.X, padx=5, pady=5)
        self.log_path_button = PHOMODButton(
            self,
            text="Set Log Location",
            command=self.choose_log_location,
            help_text="Select a directory to save logs."
        )
        self.log_path_button.pack(padx=5, pady=5)

        self.disable_logging_check = PHOMODCheckbutton(
            self,
            text="Disable File Logging",
            variable=self.disable_logging_var,
            help_text="Disables saving logs to a file. UI logs will still be displayed.",
            command=self.on_disable_logging_change
        )
        self.disable_logging_check.pack(anchor="w", padx=5, pady=5)

        self.on_disable_logging_change()
        self.on_log_rotation_change()
        app_logger.info("🏗️ Logging Settings section created.")

    def update_file_size_entry_state(self):
        is_max_file_size = self.log_rotation_var.get() == "Max file size"
        is_disabled = self.disable_logging_var.get()
        new_state = "normal" if is_max_file_size and not is_disabled else "disabled"
        self.log_file_size_entry.config(state=new_state)

    def choose_log_location(self):
        if not self.disable_logging_var.get():
            directory = filedialog.askdirectory()
            if directory:
                self.log_path_var.set(directory)
                SETTINGS.set("logs_dir", directory)
                app_logger.info(f"📁 Log directory set to: {directory}")

    def on_log_file_size_change(self, *_):
        if self.log_rotation_var.get() == "Max file size":
            try:
                size = int(self.log_file_size_var.get())
                if size <= 0:
                    raise ValueError("File size must be positive")
                SETTINGS.set("max_log_size_mb", size)
                app_logger.info(f"📏 Max file size set to: {size}MB")
            except ValueError:
                app_logger.warning("⚠️ Invalid file size entered. Please enter a positive integer.")

    def on_log_rotation_change(self, *_):
        SETTINGS.set("log_rotation", self.log_rotation_var.get())
        app_logger.info(f"🔄 Log rotation updated: {self.log_rotation_var.get()}")
        self.update_file_size_entry_state()

    def on_disable_logging_change(self, *_):
        is_disabled = self.disable_logging_var.get()
        self.log_rotation_menu.config(state="disabled" if is_disabled else "readonly")
        self.log_path_entry.config(state="disabled" if is_disabled else "readonly")
        self.log_path_button.config(state="disabled" if is_disabled else "normal")
        SETTINGS.set("disable_file_logging", is_disabled)
        app_logger.info(f"📢 File logging toggled: {'Disabled' if is_disabled else 'Enabled'}")
        self.update_file_size_entry_state()

    def on_log_level_change(self, *_):
        new_level = self.log_level_var.get()
        SETTINGS.set("log_level", new_level)
        log_level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        app_logger.setLevel(log_level_map.get(new_level, logging.INFO))
        app_logger.info(f"🔊 Log level changed to {new_level}")


# ----------------------------------------------------------------------------------------------------------------------
#                                     Workspace Control Settings Section 📂
# ----------------------------------------------------------------------------------------------------------------------
class WorkspaceControlSettingsSection(BaseSettingsSection):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Tab Control", "Hide or show certain workspaces.")
        self.hidden_workspaces = {}
        self.required_workspaces = {"Project", "Settings"}  # Required workspaces cannot be hidden
        self._build()

    def _build(self):
        workspaces_check_frame = PHOMODFrame(self)
        workspaces_check_frame.pack(fill=tk.X, padx=5, pady=5)
        available_workspaces = self.controller.workspace_manager.get_available_workspaces()
        for workspace_label in available_workspaces:
            if workspace_label not in self.required_workspaces:
                self.hidden_workspaces[workspace_label] = tk.BooleanVar(value=False)
                PHOMODCheckbutton(
                    workspaces_check_frame,
                    text=f"Hide {workspace_label}",
                    command=self.apply_workspace_visibility,
                    variable=self.hidden_workspaces[workspace_label],
                    help_text=f"Toggle visibility of the {workspace_label} workspace."
                ).pack(anchor="w", padx=5, pady=2)
        app_logger.info("🏗️ Tab Control section created.")

    def apply_workspace_visibility(self):
        for workspace_label, var in self.hidden_workspaces.items():
            if var.get():
                self.controller.workspace_manager.hide_workspace(workspace_label)
            else:
                self.controller.workspace_manager.show_workspace(workspace_label)


# ----------------------------------------------------------------------------------------------------------------------
#                                     Advanced Options Settings Section 🔧
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
        app_logger.info("🏗️ Advanced Options section created.")


# ----------------------------------------------------------------------------------------------------------------------
#                                             About Section ℹ️
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
        app_logger.info("🏗️ About section created.")


# ----------------------------------------------------------------------------------------------------------------------
#                                             Main Settings Panel View 🏠
# ----------------------------------------------------------------------------------------------------------------------
class SettingsPanelView(PHOMODScrollableFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        app_logger.info(f"🚦 Initializing {self.__class__.__name__}")
        self.controller = controller
        self._populate_sections()
        self.after(0, self._apply_current_theme)
        self.controller.update_status_bar_text("🛠️ Settings loaded successfully!")


    def _populate_sections(self):
        ThemeSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        UpdateSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        UIAccessibilitySettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        FileDataSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        LoggingSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        WorkspaceControlSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        AdvancedSettingsSection(self.inner_frame, self.controller).pack(fill=tk.X, padx=5, pady=10)
        AboutSection(self.inner_frame, self.controller).pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

    def _apply_current_theme(self):
        """Ensures that the current theme is applied after all sections are built."""
        theme = self.controller.theme_manager.get_theme() or "Arc"
        applied_theme = self.controller.theme_manager.apply_theme(theme, force=True)
        if applied_theme is None:
            app_logger.warning("⚠️ Failed to apply theme; falling back to 'Arc'.")
            self.controller.theme_manager.apply_theme("Arc", force=True)
