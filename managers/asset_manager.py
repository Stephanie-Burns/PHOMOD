import os
from PIL import Image, ImageTk
import logging
from typing import Dict, Tuple, Optional

app_logger = logging.getLogger("PHOMODLogger")

class AssetManager:
    """Handles caching and retrieval of assets such as icons."""
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self._cache: Dict[str, ImageTk.PhotoImage] = {}
        self._placeholder_icon = None

    def get_icon(self, icon_name: Optional[str], size: Tuple[int, int] = (16, 16)) -> ImageTk.PhotoImage:
        if not icon_name:
            return self._get_placeholder_icon(size)
        icon_path = os.path.join(self.assets_path, icon_name)
        if icon_path in self._cache:
            return self._cache[icon_path]
        if not os.path.exists(icon_path):
            app_logger.warning(f"⚠️ Icon '{icon_name}' not found. Using placeholder.")
            return self._get_placeholder_icon(size)
        try:
            img = Image.open(icon_path).resize(size, Image.Resampling.LANCZOS)
            self._cache[icon_path] = ImageTk.PhotoImage(img)
            return self._cache[icon_path]
        except Exception as e:
            app_logger.error(f"❌ Failed to load icon '{icon_name}': {e}")
            return self._get_placeholder_icon(size)

    def _get_placeholder_icon(self, size=(16, 16)) -> ImageTk.PhotoImage:
        if self._placeholder_icon is None:
            self._placeholder_icon = ImageTk.PhotoImage(Image.new("RGBA", size, (0, 0, 0, 0)))
        return self._placeholder_icon

    def clear_cache(self):
        self._cache.clear()
        app_logger.info("🔄 Asset cache cleared.")
