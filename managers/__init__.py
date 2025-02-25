
from .help_text_manager import HelpTextManager
from .sidebar_manager import SidebarManager
from .theme_manager import ThemeManager
from .workspace_manager import WorkspaceManager
from .log_manager import LogManager


__all__ = [
    "HelpTextManager",
    "SidebarManager",
    "ThemeManager",
    "WorkspaceManager",
    "LogManager",
]

print("Managers __init__ loaded; LogManager =", LogManager)
