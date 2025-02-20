Example Scenarios
Example 1: Standard
Copy
Edit
MyMod/
   ├── Data Files/
   └── Readme.txt
✅ No problem! Step: MyMod → Group: MyMod → Plugin: MyMod → Points to Data Files.

Example 2: Forgotten Data Files
Copy
Edit
MyMod/
   ├── meshes/
   ├── textures/
   ├── icons/
   ├── Readme.txt
👀 User forgot Data Files/
🛠 We treat this as:

Copy
Edit
MyMod/
   ├── Data Files/
   │    ├── meshes/
   │    ├── textures/
   │    ├── icons/
   └── Readme.txt
✅ Fixed!
Step: MyMod → Group: MyMod → Plugin: MyMod → Points to Data Files

Example 3: Mixed Folder Structure
Copy
Edit
MyMod/
   ├── UI Overhaul/
   │    ├── Data Files/
   │    ├── mwse/
   │    ├── textures/
   │    ├── scripts/
   │    ├── Readme.txt
👀 Contains both Data Files/ and loose folders
🛠 We prioritize Data Files/, but also move mwse/, textures/, and scripts/ under it.

Copy
Edit
MyMod/
   ├── UI Overhaul/
   │    ├── Data Files/
   │    │    ├── mwse/
   │    │    ├── textures/
   │    │    ├── scripts/
   │    ├── Readme.txt
✅ Fixed!
Step: MyMod → Group: UI Overhaul → Plugin: UI Overhaul → Points to Data Files
