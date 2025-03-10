### PHOMOD UI Development Plan (TTK)

#### Overview
PHOMOD is a FOMOD generator with a **non-destructive philosophy**. The UI should be **clear, intuitive, and visually appealing** while allowing users to manage their mod projects **without typing paths manually**.

---

## 1. Core Design Principles
- **Modular UI:** Each component (file browser, treeview, settings) should be **self-contained**.
- **Drag & Drop Support:** Users should be able to drop mod folders/images directly.
- **Customization-Friendly:** Support for **themes, color selection, and backgrounds**.
- **Easy Rearrangement:** Frames should be flexible, allowing **layout modifications**.
- **File Validation & XML Generation:** Ensure we **don't require rework** of the backend.

---

## 2. UI Layout (Planned in TTK)
### Main Window
📂 **Project Selection Frame**
- Directory picker (with recent projects)
- Drag-and-drop support for mod folders

🗂️ **Sidebar Navigation (Tabs/Tree)**
- Projects List (if workspace mode is enabled)
- Current Mod Structure

📜 **Treeview Structure Display**
- Steps, Groups, Plugins (as a tree)
- **Right-click edit menu** for modifying details

🎨 **Edit Panel**
- Image selector (with preview)
- Description editor (auto-updates XML)
- Mod type selection (optional)

⚙️ **Settings Menu**
- Theme selection (Trans flag colors default!)
- Custom background support
- Output directory settings

📜 **XML Preview & Export**
- Inline XML validation
- Export button to package everything

---

## 3. Feature Breakdown
| Feature | Details |
|---------|---------|
| **File Browser** | Directory selection **+ drag-and-drop** support |
| **Treeview Editor** | Represents **Steps, Groups, Plugins**, allowing easy reordering |
| **Mod Details Editor** | Modify **descriptions, images, plugin types** directly |
| **Theme & Layout Customization** | Users can **change colors, fonts, and layout positions** |
| **FOMOD XML Generation** | Full control over **FOMOD config creation** |
| **Non-Destructive Workflow** | Never overwrites user data **unless explicitly confirmed** |
| **Mod Packaging** | Archive mods into **structured zips** for easy distribution |
