
import logging
import threading
import tkinter as tk
from tkinter import messagebox

from phomod_widgets import (
    PHOMODFrame, PHOMODLabel, PHOMODComboBox, PHOMODButton,
    PHOMODLabelFrame, PHOMODCheckbutton, PHOMODEntry
)

app_logger = logging.getLogger('FOMODLogger')

class SettingsTab(PHOMODFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        self.controller = controller
        self.create_scrollable_widgets()
        app_logger.info("SettingsTab initialized.")
        self.controller.update_status_bar_text("🛠️ Settings loaded successfully!")

    def create_scrollable_widgets(self):
        """Creates a scrollable frame for settings."""
        container = PHOMODFrame(self)
        container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vsb = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Create an inner frame to hold all settings widgets
        self.inner_frame = PHOMODFrame(self.canvas, controller=self.controller)
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse wheel event
        self.inner_frame.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.inner_frame.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.create_widgets_in_inner()

    def _bind_mousewheel(self):
        """Binds mouse wheel scrolling to the canvas and all widgets inside inner_frame."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux (scroll down)

        # Bind mouse wheel event to all child widgets inside the frame
        for widget in self.inner_frame.winfo_children():
            widget.bind("<Enter>", lambda e: self._bind_mousewheel())
            widget.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _unbind_mousewheel(self):
        """Unbinds the mouse wheel event when cursor leaves."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Handles the mouse wheel scrolling."""
        if event.num == 5 or event.delta < 0:  # Scroll down (Linux or Windows)
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Scroll up (Linux or Windows)
            self.canvas.yview_scroll(-1, "units")

    def _on_frame_configure(self, event):
        """Updates scroll region when the inner frame resizes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ensures the inner window resizes correctly."""
        self.canvas.itemconfigure(self.inner_window, width=event.width)

    def create_widgets_in_inner(self):
        """Creates all settings widgets inside the scrollable frame."""
        self.create_theme_settings()
        self.create_logging_settings()
        self.create_update_settings()
        self.create_language_settings()
        self.create_about_section()

        self.after(0, lambda: self.apply_theme(None))
        app_logger.info("SettingsTab widgets created successfully.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                 🎨 Theme Settings
    # ------------------------------------------------------------------------------------------------------------------
    def create_theme_settings(self):
        theme_frame = PHOMODLabelFrame(
            self.inner_frame, text="Theme Selection", help_text="Change the application's theme."
        )
        theme_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)

        theme_options = self.controller.theme_manager.get_theme_options()
        self.theme_var = tk.StringVar(value="Default")

        self.theme_menu = PHOMODComboBox(
            theme_frame, textvariable=self.theme_var, values=theme_options, state="readonly",
            help_text="Select a theme for the application interface."
        )
        self.theme_menu.pack(fill=tk.X, padx=5, pady=5)
        self.theme_menu.bind("<<ComboboxSelected>>", self.apply_theme)

        self.current_theme_label = PHOMODLabel(
            theme_frame, font=self.controller.fonts["italic"],
            text=f"Current Theme: {self.controller.theme_manager.get_theme()}",
            help_text="Displays the currently active theme."
        )
        self.current_theme_label.pack(pady=5)

        app_logger.info("Theme selection section created.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                               📜 Logging Settings
    # ------------------------------------------------------------------------------------------------------------------
    def create_logging_settings(self):
        log_frame = PHOMODLabelFrame(
            self.inner_frame, text="Logging Settings", help_text="Adjust logging settings and levels."
        )
        log_frame.pack(fill=tk.X, padx=5, pady=10, expand=True)

        PHOMODLabel(log_frame, text="Log Level:", help_text="Choose the level of detail for logs.").pack(
            anchor="w", padx=5, pady=(5, 10)
        )

        self.log_level_var = tk.StringVar(value="INFO")
        self.log_level_menu = PHOMODComboBox(
            log_frame, textvariable=self.log_level_var, state="readonly",
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help_text="Select the minimum log level for displayed logs."
        )
        self.log_level_menu.pack(fill=tk.X, padx=5, pady=(5, 10))

        PHOMODButton(
            log_frame, text="Configure Rotation", help_text="Set up automatic log rotation.",
            command=self.configure_log_rotation
        ).pack(padx=5, pady=(5, 10))

        app_logger.info("Logging settings section created.")

    def configure_log_rotation(self):
        """Handles log rotation configuration."""
        self.controller.update_status_bar_text("Log rotation configuration is not yet implemented.")
        app_logger.info("Configure log rotation button pressed.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                🔄 Update Settings
    # ------------------------------------------------------------------------------------------------------------------
    def create_update_settings(self):
        update_frame = PHOMODLabelFrame(
            self.inner_frame, text="Update Settings", help_text="Configure automatic update checks."
        )
        update_frame.pack(fill=tk.X, padx=5, pady=10, expand=True)

        self.auto_update_var = tk.BooleanVar(value=True)

        PHOMODCheckbutton(
            update_frame, text="Automatically check for updates", variable=self.auto_update_var,
            help_text="Enable or disable automatic update checks."
        ).pack(anchor="w", padx=5, pady=5)

        PHOMODButton(
            update_frame, text="Check Now", help_text="Manually check for updates.",
            command=self.check_for_updates,
        ).pack(padx=5, pady=(5, 10))

        app_logger.info("Update settings section created.")

    def check_for_updates(self):
        """Simulates checking for updates."""
        self.controller.update_status_bar_text("Checking for updates...")
        app_logger.info("Checking for updates...")
        threading.Timer(2.0, lambda: self.controller.update_status_bar_text("No updates available.")).start()
        app_logger.info("Update check completed.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                               🌎 Language Settings
    # ------------------------------------------------------------------------------------------------------------------
    def create_language_settings(self):
        lang_frame = PHOMODLabelFrame(
            self.inner_frame, text="Language", help_text="Set the application language."
        )
        lang_frame.pack(fill=tk.X, padx=5, pady=10, expand=True)

        PHOMODLabel(lang_frame, text="Select Language:", help_text="Choose a language for the UI.").pack(
            anchor="w", padx=5, pady=(5, 0)
        )

        self.lang_var = tk.StringVar(value="English")
        self.lang_menu = PHOMODComboBox(
            lang_frame, textvariable=self.lang_var, values=["English", "Spanish", "French", "German"],
            state="readonly", help_text="Select the language for the application."
        )
        self.lang_menu.pack(fill=tk.X, padx=5, pady=5)

        PHOMODButton(
            lang_frame, text="Help Translate", help_text="Assist in translating the app into other languages.",
            command=self.ask_for_translation_help
        ).pack(padx=5, pady=(5, 10))

        app_logger.info("Language settings section created.")

    def ask_for_translation_help(self):
        """Opens a dialog for translation assistance."""
        self.controller.update_status_bar_text("Translation help requested.")
        app_logger.info("Translation help button pressed.")
        messagebox.showinfo("Translation Help", "Please visit our GitHub page to contribute translations.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                  ℹ️ About Section
    # ------------------------------------------------------------------------------------------------------------------
    def create_about_section(self):
        about_frame = PHOMODLabelFrame(
            self.inner_frame, text="About", help_text="View information about PHOMOD."
        )
        about_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        about_text = (
            "PHOMOD - Mod Organizer\nVersion 1.0\n\n"
            "Developed by Stephanie Burns\n"
            "Visit the GitHub repository for more info!"
        )

        PHOMODLabel(about_frame, text=about_text, help_text="Application version and credits.",
                     anchor="center", justify="center").pack(expand=True, padx=5, pady=5)

        app_logger.info("About section created.")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                 🎭 Helper Methods
    # ------------------------------------------------------------------------------------------------------------------
    def apply_theme(self, event=None):
        selected_theme = self.theme_var.get()
        if selected_theme == self.controller.theme_manager.separator:
            self.controller.update_status_bar_text("Please select a valid theme.")
            return

        applied_theme = self.controller.theme_manager.apply_theme(selected_theme)
        self.current_theme_label.config(text=f"Current Theme: {applied_theme}")
        self.controller.update_status_bar_text(f"Theme set to {applied_theme}.")
        app_logger.info(f"Theme applied: {applied_theme}")
