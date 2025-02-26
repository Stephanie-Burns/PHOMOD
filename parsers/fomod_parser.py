
import os
import re
import shutil
import zipfile
import datetime

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

from appdata import phomod_map


# Common folders inside "Data Files" in Morrowind
MORROWIND_DATA_FOLDERS = {"meshes", "icons", "textures", "music", "sound", "splash", "bookart", "fonts", "scripts", "mwse"}

def clean_name(name: str) -> str:
    """ Removes leading numbers and trims spaces from folder names. """
    return re.sub(r"^\d+\s*", "", name).strip()

class FomodEntry:
    """ Base class representing an entry in the FOMOD structure. """
    def __init__(self, name: str):
        self.name = clean_name(name)

class Step(FomodEntry):
    """ Represents a FOMOD installation step. """
    def __init__(self, name: str):
        super().__init__(name)
        self.groups = []

    def add_group(self, group):
        self.groups.append(group)

class Group(FomodEntry):
    """ Represents a FOMOD group, which holds plugins. """
    def __init__(self, name: str):
        super().__init__(name)
        self.plugins = []

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

class Plugin(FomodEntry):
    """ Represents a FOMOD plugin, which contains files. """
    def __init__(self, name: str, absolute_path: str, base_path: str,
                 image_path: str = None, description: str = None, type_descriptor: str = None):
        super().__init__(name)
        self.absolute_path = absolute_path  # Full system path
        self.relative_path = os.path.relpath(absolute_path, base_path).replace("/", "\\")  # Relative path for XML
        self.image_path = image_path  # Optional image path
        self.description = description
        self.type_descriptor = type_descriptor

class FomodParser:
    """ Handles directory parsing and structuring for FOMOD. """
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.steps = []

    def parse(self):
        """ Parses the given directory into steps, groups, and plugins. """
        root_name = clean_name(os.path.basename(self.root_dir))
        root_step = Step(root_name)

        for item in sorted(os.listdir(self.root_dir)):
            full_path = os.path.join(self.root_dir, item)
            if item.lower() == "fomod":
                continue
            if os.path.isdir(full_path):
                self.parse_group_or_plugin(root_step, full_path)

        self.steps.append(root_step)

    def parse_group_or_plugin(self, step: Step, path: str):
        """ Determines if a directory is a Group or Plugin. """
        folder_name = clean_name(os.path.basename(path))
        contents = {name.lower() for name in os.listdir(path)}

        if "data files" in contents:
            # If the folder contains a "Data Files" directory, it's a Plugin
            plugin = Plugin(folder_name, os.path.join(path, "Data Files"), self.root_dir)
            group = Group(folder_name)  # A plugin must belong to a group
            group.add_plugin(plugin)

            if isinstance(step, Step):  # Ensure only Steps can contain groups
                step.add_group(group)

        elif contents & MORROWIND_DATA_FOLDERS:
            # If the folder contains Morrowind files but no "Data Files", treat it as a Plugin
            plugin = Plugin(folder_name, path, self.root_dir)
            group = Group(folder_name)
            group.add_plugin(plugin)

            if isinstance(step, Step):  # Only Steps can contain groups
                step.add_group(group)

        else:
            # Otherwise, it's a Group
            group = Group(folder_name)
            for sub_item in sorted(os.listdir(path)):
                full_sub_path = os.path.join(path, sub_item)
                if os.path.isdir(full_sub_path):
                    self.parse_group_or_plugin(group, full_sub_path)  # Ensure we are only adding plugins

            if isinstance(step, Step):  # Only Steps can contain groups
                step.add_group(group)



class FomodXMLWriter:
    """ Generates FOMOD XML from parsed structure. """

    def __init__(self, steps):
        self.steps = steps

    def generate_xml(self) -> str:
        """ Generates and returns the XML content as a formatted string. """
        fomod_root = self._create_root_element()
        install_steps = self._create_install_steps(fomod_root, self.steps)

        for step in self.steps:
            self._add_step(install_steps, step)

        return self._format_xml(fomod_root)

    @staticmethod
    def _create_root_element() -> ET.Element:
        """ Creates the root config element with XML schema. """
        return ET.Element("config", {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:noNamespaceSchemaLocation": "http://qconsulting.ca/fo3/ModConfig5.0.xsd"
        })

    @staticmethod
    def _create_install_steps(root: ET.Element, steps) -> ET.Element:
        """ Adds the <installSteps> element to the root config. """
        module_name = ET.SubElement(root, "moduleName")
        module_name.text = steps[0].name if steps else "Unnamed Mod"
        return ET.SubElement(root, "installSteps", order="Explicit")

    @staticmethod
    def _add_step(parent: ET.Element, step) -> None:
        """ Adds an install step element to the parent. """
        step_element = ET.SubElement(parent, "installStep", name=step.name)
        file_groups = ET.SubElement(step_element, "optionalFileGroups", order="Explicit")

        for group in step.groups:
            FomodXMLWriter._add_group(file_groups, group)

    @staticmethod
    def _add_group(parent: ET.Element, group) -> None:
        """ Adds a group element to the parent. """
        group_element = ET.SubElement(parent, "group", name=group.name, type="SelectAny")
        plugins = ET.SubElement(group_element, "plugins", order="Explicit")

        for plugin in group.plugins:
            FomodXMLWriter._add_plugin(plugins, plugin)

    @staticmethod
    def _add_plugin(parent: ET.Element, plugin) -> None:
        """ Adds a plugin element to the parent. """
        plugin_element = ET.SubElement(parent, "plugin", name=plugin.name)

        if plugin.image_path:
            ET.SubElement(plugin_element, "image", path=plugin.image_path.replace("/", "\\"))

        description = ET.SubElement(plugin_element, "description")
        description.text = plugin.description or "Auto-generated description."

        files = ET.SubElement(plugin_element, "files")
        ET.SubElement(files, "folder", source=plugin.relative_path, destination="\\", priority="0")

        type_descriptor = ET.SubElement(plugin_element, "typeDescriptor")
        ET.SubElement(type_descriptor, "type", name=plugin.type_descriptor or "Optional")

    @staticmethod
    def _format_xml(root: ET.Element) -> str:
        """ Converts an XML tree to a pretty-formatted string. """
        return parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="  ")


class FomodFileManager:
    """ Handles file operations related to FOMOD, ensuring non-destructive modifications. """

    def __init__(self, root_dir: str, output_dir: str = None, keep_existing_output: bool = True):
        self.root_dir = root_dir
        self.mod_name = os.path.basename(os.path.normpath(root_dir))
        self.keep_existing_output = keep_existing_output

        # Define output location, with versioning if needed
        base_output_dir = output_dir or os.path.join(os.path.dirname(root_dir), "fomod_output")
        self.output_dir = self._resolve_output_path(base_output_dir)

        self.fomod_dir = os.path.join(self.output_dir, "fomod")
        self.fomod_config_path = os.path.join(self.fomod_dir, "ModuleConfig.xml")

        os.makedirs(self.fomod_dir, exist_ok=True)

    def _resolve_output_path(self, base_output_dir):
        """ Determines the correct output path, handling versioning if needed. """
        if not self.keep_existing_output:
            return os.path.join(base_output_dir, self.mod_name)

        # Generate a timestamped directory
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M__%S")
        return os.path.join(base_output_dir, f"{self.mod_name}_{timestamp}")

    def write_fomod_config(self, xml_content: str):
        """ Writes the generated XML content to the FOMOD configuration file. """
        with open(self.fomod_config_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

    def generate_new_structure(self):
        """ Creates a FOMOD-ready workspace without modifying the original files. """
        if not self.keep_existing_output and os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)  # Remove old output if overwriting
        shutil.copytree(self.root_dir, self.output_dir)

        # Ensure 'Data Files' is inside every plugin
        for root, dirs, files in os.walk(self.output_dir):
            if any(d.lower() in MORROWIND_DATA_FOLDERS for d in dirs) and "Data Files" not in dirs:
                data_files_path = os.path.join(root, "Data Files")
                os.makedirs(data_files_path, exist_ok=True)
                for d in dirs:
                    if d.lower() in MORROWIND_DATA_FOLDERS:
                        shutil.move(os.path.join(root, d), os.path.join(data_files_path, d))

    def generate_archive(self, user_version: str = None):
        """ Creates a zip archive of the structured mod. """
        base_zip_name = self.mod_name
        if user_version:
            base_zip_name += f"_{user_version}"
        elif self.keep_existing_output:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            base_zip_name += f"_{timestamp}"

        zip_path = os.path.join(os.path.dirname(self.output_dir), f"{base_zip_name}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, self.output_dir)
                    zipf.write(abs_path, rel_path)
        print(f"✅ Archive created: {zip_path}")


class FomodManager:
    """ Orchestrates parsing, XML generation, structure validation, and packaging. """

    def __init__(self, root_dir: str, output_dir: str = None, keep_existing_output: bool = True):
        self.parser = FomodParser(root_dir)
        self.xml_writer = None
        self.file_manager = FomodFileManager(root_dir, output_dir, keep_existing_output)

    def parse_fomod(self):
        """ Parses the FOMOD structure. """
        self.parser.parse()

    def generate_xml(self):
        """ Generates XML from parsed data. """
        if not self.parser.steps:
            raise ValueError("Cannot generate XML: No parsed steps available.")
        self.xml_writer = FomodXMLWriter(self.parser.steps)
        return self.xml_writer.generate_xml()

    def save_xml(self, xml_content: str):
        """ Saves the generated XML to the FOMOD directory. """
        self.file_manager.write_fomod_config(xml_content)

    def generate_new_structure(self):
        """ Creates a properly structured workspace for FOMOD packaging. """
        self.file_manager.generate_new_structure()
        print(f"✅ New FOMOD-ready structure created at {self.file_manager.output_dir}")

    def generate_archive(self, user_version: str = None):
        """ Packages the mod and FOMOD configuration into a zip. """
        self.file_manager.generate_archive(user_version)

    def run(self, generate_structure=False, generate_archive=False, user_version: str = None):
        """ Runs the full process based on options. """
        self.parse_fomod()
        xml_output = self.generate_xml()
        self.save_xml(xml_output)
        print(f"🔹 Welcome to PHOMOD: {phomod_map()}")
        print(f"✅ FOMOD XML generated successfully at {self.file_manager.fomod_config_path}")

        if generate_structure:
            self.generate_new_structure()

        if generate_archive:
            self.generate_archive(user_version)


# Run the script
if __name__ == "__main__":
    test_dir = "/home/dougr/Games/prefixes/morrowind_gog/pfx/drive_c/users/steamuser/My Documents/Dwemer Interface Suite/thetsing_delete_later/100 UI Enhancements"
    manager = FomodManager(test_dir)
    manager.run()
