## **📄 XML Writer API Documentation**

### **Overview**
The `FomodXMLWriter` class **generates a valid `ModuleConfig.xml`** for FOMOD. It ensures:
- **Properly structured steps, groups, and plugins**
- **Consistent relative paths**
- **Cleanly formatted XML**

---

### **1. Class Reference**
### **`FomodXMLWriter`**
```python
class FomodXMLWriter:
    def __init__(self, steps: List[Step])
```
**Parameters:**
- `steps (List[Step])`: The parsed mod structure, containing installation steps.

---

### **2. Methods**
#### **`generate_xml() → str`**
Generates a properly formatted **ModuleConfig.xml**.

```python
def generate_xml(self) -> str
```
**Returns:**
- A string containing the full XML content.

---

#### **`_create_root_element() → ET.Element`**
Creates the root `<config>` XML element.

```python
def _create_root_element() -> ET.Element
```

---

#### **`_create_install_steps(root: ET.Element, steps: List[Step]) → ET.Element`**
Adds the `<installSteps>` element.

```python
def _create_install_steps(root: ET.Element, steps: List[Step]) -> ET.Element
```

---

#### **`_add_step(parent: ET.Element, step: Step) → None`**
Adds an `<installStep>` entry.

```python
def _add_step(parent: ET.Element, step: Step) -> None
```

---

#### **`_add_group(parent: ET.Element, group: Group) → None`**
Adds a `<group>` entry.

```python
def _add_group(parent: ET.Element, group: Group) -> None
```

---

#### **`_add_plugin(parent: ET.Element, plugin: Plugin) → None`**
Adds a `<plugin>` entry.

```python
def _add_plugin(parent: ET.Element, plugin: Plugin) -> None
```

---

#### **`_format_xml(root: ET.Element) → str`**
Formats the XML for readability.

```python
def _format_xml(root: ET.Element) -> str
```

---
