
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


class SettingsTab(PHOMODFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        self.controller = controller
        self._create_scrollable_container()
        self._populate_sections()

        app_logger.info("SettingsTab initialized.")
        self.controller.update_status_bar_text("🛠️ Settings loaded successfully!")

    def _create_scrollable_container(self):
        """Creates the scrollable settings container using PHOMODScrollableFrame."""
        self.scrollable_frame = PHOMODScrollableFrame(self, controller=self.controller)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)
        self.inner_frame = self.scrollable_frame.inner_frame

    def _populate_sections(self):
        self._create_theme_settings()
        self._create_update_settings()
        self._create_ui_accessibility_settings()
        self._create_file_data_settings()
        self._create_logging_settings()
        self._create_tab_control_settings()
        self._create_advanced_settings()
        self._create_about_section()
        self.after(0, lambda: self.apply_theme(None))

        app_logger.info("SettingsTab sections created successfully.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                 🎨 Theme Settings
    # ------------------------------------------------------------------------------------------------------------------
    def _create_theme_settings(self):
        theme_options = self.controller.theme_manager.get_theme_options()
        current_theme = self.controller.theme_manager.get_theme()
        self.theme_var = tk.StringVar(value="Default")


        theme_title = self._create_section_title(
            self.inner_frame, "Theme Selection", "Change the application's theme."
        )
        theme_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=theme_title,
            help_text="Change the application's theme."
        )
        theme_frame.pack(fill=tk.X, padx=5, pady=20, expand=True)


        self.theme_menu = PHOMODComboBox(
            theme_frame, textvariable=self.theme_var, values=theme_options, state="readonly",
            help_text="Select a theme for the application interface."
        )
        self.theme_menu.pack(fill=tk.X, padx=5, pady=5)
        self.theme_menu.bind("<<ComboboxSelected>>", self.apply_theme)


        self.current_theme_label = PHOMODLabel(
            theme_frame, font=self.controller.fonts["italic"],
            text=f"Current Theme: {current_theme}",
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
        if not (theme_options := self.controller.theme_manager.get_theme_options()):
            return

        random_theme = random.choice(theme_options)
        self.theme_var.set(random_theme)
        self.apply_theme()

        app_logger.info(f"Random theme applied: {random_theme}")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                🔄 Update Settings
    # ------------------------------------------------------------------------------------------------------------------
    def _create_update_settings(self):
        self.auto_update_var = tk.BooleanVar(value=True)


        update_title = self._create_section_title(
            self.inner_frame, "Update Settings", "Configure automatic update checks."
        )
        update_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=update_title,
            help_text="Configure automatic update checks."
        )
        update_frame.pack(fill=tk.X, padx=5, pady=20, expand=True)



        PHOMODCheckbutton(
            update_frame, text="Automatically check for updates", variable=self.auto_update_var,
            help_text="Enable or disable automatic update checks."
        ).pack(anchor="w", padx=5, pady=5)

        PHOMODButton(
            update_frame, text="Check Now", help_text="Manually check for updates.",
            command=self.check_for_updates
        ).pack(padx=5, pady=(5, 10))


        app_logger.info("Update settings section created.")

    def check_for_updates(self):
        self.controller.update_status_bar_text("Checking for updates...")
        app_logger.info("Checking for updates...")
        threading.Timer(2.0, lambda: self.controller.update_status_bar_text("No updates available.")).start()
        app_logger.info("Update check completed.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                              🌎 UI & Accessibility
    # ------------------------------------------------------------------------------------------------------------------
    def _create_ui_accessibility_settings(self):
        self.language_var = tk.StringVar(value="English")
        self.font_size_var = tk.StringVar(value="Normal")


        ui_title = self._create_section_title(
            self.inner_frame, "UI & Accessibility", "Customize interface settings."
        )
        ui_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=ui_title,
            help_text="Customize interface settings."
        )
        ui_frame.pack(fill=tk.X, padx=5, pady=20, expand=True)


        PHOMODLabel(
            ui_frame, text="Language:", help_text="Select UI language."
        ).pack(anchor="w", padx=5, pady=2)

        self.language_menu = PHOMODComboBox(
            ui_frame, textvariable=self.language_var,
            values=["English", "Spanish", "French", "German"],
            state="readonly", help_text="Select the language for the application."
        )
        self.language_menu.pack(fill=tk.X, padx=5, pady=5)


        PHOMODLabel(
            ui_frame, text="Font Size:", help_text="Adjust font size for readability."
        ).pack(anchor="w", padx=5, pady=2)

        self.font_size_menu = PHOMODComboBox(
            ui_frame, textvariable=self.font_size_var,
            values=["Small", "Normal", "Large"],
            state="readonly", help_text="Select the font size for the UI."
        )
        self.font_size_menu.pack(fill=tk.X, padx=5, pady=5)


        PHOMODButton(
            ui_frame, text="Help Translate", help_text="Assist in translating the app into other languages.",
            command=self.ask_for_translation_help
        ).pack(padx=5, pady=5)


        app_logger.info("UI & Accessibility section created.")

    def ask_for_translation_help(self):
        self.controller.update_status_bar_text("Translation help requested.")
        app_logger.info("Translation help button pressed.")
        messagebox.showinfo("Translation Help", "Please visit our GitHub page to contribute translations.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                          🗄 File & Data Management
    # ------------------------------------------------------------------------------------------------------------------
    def _create_file_data_settings(self):
        self.starting_dir_var = tk.StringVar(value="Not Set")


        file_title = self._create_section_title(
            self.inner_frame, "File & Data Management", "Manage file paths and directories."
        )
        file_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=file_title,
            help_text="Manage file paths and directories."
        )
        file_frame.pack(fill=tk.X, padx=5, pady=20, expand=True)


        PHOMODLabel(
            file_frame, text="Default Starting Directory:", help_text="Set a default working directory."
        ).pack(anchor="w", padx=5, pady=2)

        PHOMODEntry(
            file_frame, textvariable=self.starting_dir_var, state="readonly"
        ).pack(fill=tk.X, padx=5, pady=5)

        PHOMODButton(
            file_frame, text="Set Directory", command=self.choose_starting_directory,
            help_text="Select a default directory."
        ).pack(padx=5, pady=5)


        app_logger.info("File & Data Management section created.")

    def choose_starting_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.starting_dir_var.set(directory)

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                               📜 Logging Settings
    # ------------------------------------------------------------------------------------------------------------------
    def _create_logging_settings(self):
        self.disable_logging_var = tk.BooleanVar(value=False)
        self.log_rotation_var = tk.StringVar(value="Daily")
        self.log_path_var = tk.StringVar(value="Not Set")


        log_title = self._create_section_title(
            self.inner_frame, "Logging Settings", "Configure logging preferences."
        )
        log_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=log_title,
            help_text="Configure logging preferences."
        )
        log_frame.pack(fill=tk.X, padx=5, pady=20, expand=True)


        PHOMODLabel(
            log_frame, text="Log Rotation:", help_text="Select log rotation frequency."
        ).pack(anchor="w", padx=5, pady=2)

        self.log_rotation_menu = PHOMODComboBox(
            log_frame, textvariable=self.log_rotation_var, values=["Daily", "Weekly", "Max file size"],
            state="readonly", help_text="Select how frequently logs rotate."
        )
        self.log_rotation_menu.pack(fill=tk.X, padx=5, pady=5)


        PHOMODLabel(
            log_frame, text="Log File Location:", help_text="Choose where logs are stored."
        ).pack(anchor="w", padx=5, pady=2)

        PHOMODEntry(
            log_frame, textvariable=self.log_path_var, state="readonly"
        ).pack(fill=tk.X, padx=5, pady=5)

        PHOMODButton(
            log_frame, text="Set Log Location", command=self.choose_log_location,
            help_text="Select a directory to save logs."
        ).pack(padx=5, pady=5)


        PHOMODCheckbutton(
            log_frame, text="Disable Logging", variable=self.disable_logging_var,
            help_text="Turn off logging entirely."
        ).pack(anchor="w", padx=5, pady=5)


        app_logger.info("Logging Settings section created.")

    def choose_log_location(self):
        directory = filedialog.askdirectory()
        if directory:
            self.log_path_var.set(directory)

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                           📂 Tab Control Settings
    # ------------------------------------------------------------------------------------------------------------------
    def _create_tab_control_settings(self):
        self.hidden_tabs = {}
        self.required_tabs = {"Project", "Settings"}


        tab_control_title = self._create_section_title(
            self.inner_frame, "Tab Control", "Hide or show certain tabs."
        )
        tab_control_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=tab_control_title,
            help_text="Hide or show certain tabs."
        )
        tab_control_frame.pack(fill=tk.X, padx=5, pady=20, expand=True)


        tab_check_frame = PHOMODFrame(tab_control_frame)
        tab_check_frame.pack(fill=tk.X, padx=5, pady=5)
        self._populate_tab_checkboxes(tab_check_frame)


        app_logger.info("Tab Control section created.")

    def _populate_tab_checkboxes(self, parent):
        """Helper method to create checkboxes for toggling tab visibility."""
        for tab in self.controller.get_available_tabs():
            if tab not in self.required_tabs:
                self.hidden_tabs[tab] = tk.BooleanVar(value=False)
                PHOMODCheckbutton(
                    parent, text=f"Hide {tab}", command=self.apply_tab_visibility,
                    variable=self.hidden_tabs[tab], help_text=f"Toggle visibility of the {tab} tab."
                ).pack(anchor="w", padx=5, pady=2)

    def apply_tab_visibility(self):
        for tab, var in self.hidden_tabs.items():
            if var.get():
                self.controller.show_tab(tab)
            else:
                self.controller.hide_tab(tab)

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                               🔧 Advanced Options
    # ------------------------------------------------------------------------------------------------------------------
    def _create_advanced_settings(self):
        self.developer_mode_var = tk.BooleanVar(value=False)


        adv_title = self._create_section_title(
            self.inner_frame, "Advanced Options", "Enable additional debugging tools."
        )
        adv_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=adv_title,
            help_text="Enable additional debugging tools."
        )
        adv_frame.pack(fill=tk.X, padx=5, pady=20, expand=True)


        PHOMODCheckbutton(
            adv_frame, text="Developer Mode", variable=self.developer_mode_var,
            help_text="Enables additional debugging options."
        ).pack(anchor="w", padx=5, pady=5)


        app_logger.info("Advanced Options section created.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                  ℹ️ About Section
    # ------------------------------------------------------------------------------------------------------------------
    def _create_about_section(self):
        about_text = (
            "PHOMOD - Mod Organizer\nVersion 1.0\n\n"
            "Developed by Stephanie Burns\n"
            "Visit the GitHub repository for more info!"
        )


        about_title = self._create_section_title(
            self.inner_frame, "About", "View information about PHOMOD."
        )
        about_frame = PHOMODLabelFrame(
            self.inner_frame, controller=self.controller, label_widget=about_title,
            help_text="View information about PHOMOD."
        )
        about_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=20)


        PHOMODLabel(
            about_frame, text=about_text, help_text="Application version and credits.",
            anchor="center", justify="center"
        ).pack(expand=True, padx=5, pady=10)


        app_logger.info("About section created.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                 🎭 Helper Methods
    # ------------------------------------------------------------------------------------------------------------------
    def _create_section_title(self, parent, text, help_text=None):
        title_label = PHOMODLabel(
            parent, text=text, font=self.controller.fonts["title"], help_text=help_text
        )


        app_logger.info(f"Section title created: {text}")

        return title_label
