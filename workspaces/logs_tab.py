
import logging
import tkinter as tk

from phomod_widgets import PHOMODFrame
from managers.log_manager import LogManager

app_logger = logging.getLogger("PHOMODLogger")

class LogsTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info(f"🚦 Initializing {self.__class__.__name__}")
        self.log_manager = LogManager(max_buffer=100)
        self.create_widgets()
        self.log_manager.attach_text_handler(self.log_text)
        self.create_context_menu()
        self.log_manager.flush_buffer_to_widget(self.log_text)

    def create_widgets(self):
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        log_font = ("Courier", 11)
        self.log_text = tk.Text(
            text_frame, wrap=tk.WORD, state="disabled",
            bg="black", fg="white", font=log_font, spacing1=4, spacing3=4
        )
        scrollbar = tk.Scrollbar(text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Set up tags for syntax highlighting
        self.log_text.tag_configure("info", foreground="lightblue")
        self.log_text.tag_configure("debug", foreground="gray")
        self.log_text.tag_configure("warning", foreground="yellow")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("critical", foreground="magenta", font=("Courier", 11, "bold"))
        self.log_text.bind("<Button-3>", self.show_context_menu)
        self.log_text.bind("<Control-Button-1>", self.show_context_menu)
        app_logger.info("LogsTab widgets created")

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_text)
        self.context_menu.add_command(label="Clear Logs", command=self.clear_logs)
        self.context_menu.add_command(label="Save Logs", command=lambda: self.log_manager.save_logs_to_file(self.log_text))

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_text(self):
        try:
            selected = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            pass

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
