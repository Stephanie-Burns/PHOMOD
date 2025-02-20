## **📄 FileHandler API Documentation**

### **Overview**
The `FileHandler` class manages **file operations** for FOMOD, ensuring a **non-destructive workflow**. It handles:
- **Writing the FOMOD XML**
- **Generating a structured workspace**
- **Packaging the mod as a zip archive**
- **Automatically handling versioned output**

---

### **1. Class Reference**
### **`FileHandler`**
```python
class FileHandler:
    def __init__(self, root_dir: str, output_dir: str = None, keep_existing_output: bool = True)
```
**Parameters:**
- `root_dir (str)`: The root directory of the mod.
- `output_dir (str, optional)`: The directory where output files will be stored. Defaults to `"fomod_output"` in the parent directory.
- `keep_existing_output (bool)`: If `True`, creates a **timestamped** output directory instead of overwriting.

---

### **2. Methods**
#### **`write_fomod_config(xml_content: str) → None`**
Writes the generated **ModuleConfig.xml** file to the FOMOD directory.

```python
def write_fomod_config(self, xml_content: str)
```
- **xml_content (str)**: The XML string to be written.

---

#### **`generate_new_structure() → None`**
Creates a **non-destructive workspace** that mirrors the original mod structure while correcting missing `Data Files/` placements.

```python
def generate_new_structure(self)
```
**Behavior:**
- Ensures `"Data Files/"` is present for every plugin.
- Moves misplaced Morrowind-specific folders (e.g., `meshes`, `textures`) into `"Data Files/"`.
- If `keep_existing_output=False`, it **overwrites** the existing output folder.

---

#### **`generate_archive(user_version: str = None) → None`**
Creates a **zip archive** of the structured mod.

```python
def generate_archive(self, user_version: str = None)
```
**Parameters:**
- `user_version (str, optional)`: A custom version label (e.g., `"1.2"`). If `None`, uses a **timestamped** version.

**Output Format:**
```
ModName_YYYY-MM-DD_HH-MM.zip
```

---
