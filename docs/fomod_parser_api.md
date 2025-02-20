### **FOMOD Parser API Documentation**

#### **Overview**
This module parses a mod directory structure and generates a `ModuleConfig.xml` file in a `fomod` folder, following FOMOD installer conventions. It automatically organizes mod components into **Steps, Groups, and Plugins**, ensuring proper FOMOD compatibility.

---

## **1. Installation & Setup**
### **Requirements**
- Python 3.6+
- Standard library (`os`, `xml.etree.ElementTree`, `re`)
- Ensure that your mod follows a logical folder structure

### **Usage Example**
To use the parser, call the `FomodManager` on the root mod directory:

```python
from fomod_parser import FomodManager

mod_directory = "/path/to/mod/root"
manager = FomodManager(mod_directory)
manager.run()
```
This will:
- Analyze the mod directory
- Generate a `fomod/ModuleConfig.xml`
- Ensure relative paths are used in the XML

---

## **2. Core Concepts**
### **Mod Structure**
FOMOD installers require a specific structure:
- **Steps**: Top-level folders containing different install groups
- **Groups**: Organize plugins under a step
- **Plugins**: The actual selectable mod components (esp/esm files, textures, meshes, etc.)

Example:
```
MyMod/
├── 100 UI Enhancements/  # Step
│   ├── 110 Minimal UI/   # Group
│   │   ├── Data Files/   # Plugin
│   ├── 120 HUD Cleaner/  # Group
│   │   ├── Data Files/   # Plugin
│   │   ├── Extra Addon/  # Plugin
│   │   │   ├── Data Files/
│   │   │   └── Readme.txt
├── fomod/ (auto-generated)
│   ├── info.xml
│   └── ModuleConfig.xml
```

---

## **3. Class Reference**
### **`FomodEntry`**
**Base class** for all entries (Steps, Groups, Plugins).
```python
class FomodEntry:
    def __init__(self, name: str)
```
- **`name`**: Cleans up the directory name by removing numeric prefixes.

---

### **`Step`**
Represents a **major installation step**.
```python
class Step(FomodEntry):
    def add_group(self, group: Group)
```
- **Holds groups** that contain actual mod files.

---

### **`Group`**
Represents a **mod option category**.
```python
class Group(FomodEntry):
    def add_plugin(self, plugin: Plugin)
```
- **Holds plugins**, which point to the actual files to install.

---

### **`Plugin`**
Represents **an installable mod component**.
```python
class Plugin(FomodEntry):
    def __init__(self, name: str, absolute_path: str, base_path: str,
                 image_path: str = None, description: str = None, type_descriptor: str = None)
```
- **`absolute_path`**: Full system path of the plugin folder.
- **`relative_path`**: Converts the path to a format compatible with FOMOD.
- **`image_path`** *(optional)*: Path to a preview image.
- **`description`** *(optional)*: Text shown in the installer.

---

### **`FomodParser`**
Parses a **directory into Steps, Groups, and Plugins**.
```python
class FomodParser:
    def __init__(self, root_dir: str)
    def parse()
```
- **`parse()`**: Detects structure and assigns categories automatically.

---

### **`FomodXMLWriter`**
Generates the **ModuleConfig.xml** file.
```python
class FomodXMLWriter:
    def generate_xml() -> str
```
- Writes **relative paths** instead of full system paths.

---

### **`FomodManager`**
Main entry point to **orchestrate parsing and XML generation**.
```python
class FomodManager:
    def run()
```
- Calls the **parser** to analyze the directory.
- Calls the **XML writer** to generate the configuration.

---

## **4. Special Cases**
| Case | Behavior |
|------|---------|
| **Only contains `Data Files/`** | Assigns the folder as a **plugin** |
| **Has multiple `Data Files/` options** | Each becomes a **separate plugin** |
| **Morrowind core directories found outside `Data Files/`** | Moves them inside `Data Files/` automatically |
| **FOMOD folder found** | **Ignored** from parsing |

---

## **5. Running Tests**
A full test suite ensures correct parsing behavior:
```bash
python -m unittest discover tests
```
Example test case:
```python
def test_fomod_structure(self):
    structure = {
        "100 UI Enhancements": {
            "110 Minimal UI": {
                "Data Files": {
                    "textures": None
                }
            }
        }
    }
    self.create_structure(structure)
    manager = FomodManager(self.test_dir)
    manager.run()
    self.assertTrue(os.path.exists(os.path.join(self.test_dir, "fomod", "ModuleConfig.xml")))
```
