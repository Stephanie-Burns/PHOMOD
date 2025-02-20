import os
import shutil
import unittest
import tempfile
from fomod_parser import FomodManager


class TestFomodParser(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "fomod_output")  # Default output location

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir)

    def create_structure(self, structure, root=None):
        """Creates a test folder structure based on a dictionary input."""
        root = root or self.test_dir
        for name, content in structure.items():
            path = os.path.join(root, name)
            if content is None:
                os.makedirs(path, exist_ok=True)
            elif isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                self.create_structure(content, path)
            else:
                with open(path, 'w') as f:
                    f.write(content)

    def get_latest_xml_path(self):
        """Finds the latest generated XML path, handling timestamped directories."""
        mod_name = os.path.basename(os.path.normpath(self.test_dir))
        mod_folders = [d for d in os.listdir(self.output_dir) if d.startswith(mod_name)]

        if not mod_folders:
            return None  # No output directory found

        # Get the most recent directory by timestamp
        latest_folder = sorted(mod_folders, reverse=True)[0]
        return os.path.join(self.output_dir, latest_folder, "fomod", "ModuleConfig.xml")

    def test_basic_fomod_structure(self):
        """Test a simple mod with just Data Files."""
        structure = {
            "Data Files": {
                "meshes": None,
                "textures": None
            }
        }
        self.create_structure(structure)
        manager = FomodManager(self.test_dir, self.output_dir)
        manager.run()

        xml_path = self.get_latest_xml_path()
        self.assertIsNotNone(xml_path, "FOMOD XML path was not found")
        self.assertTrue(os.path.exists(xml_path))

    def test_nested_groups_and_plugins(self):
        """Test a mod with groups and nested plugins."""
        structure = {
            "100 Interface Options": {
                "110 Minimal UI": {
                    "Data Files": {
                        "textures": None
                    }
                },
                "120 Inventory Styles": {
                    "Option 1 - Grid Layout": {
                        "Data Files": {
                            "meshes": None
                        }
                    },
                    "Option 2 - No Borders": {
                        "Data Files": {
                            "textures": None
                        }
                    }
                }
            }
        }
        self.create_structure(structure)
        manager = FomodManager(self.test_dir, self.output_dir)
        manager.run()

        xml_path = self.get_latest_xml_path()
        self.assertIsNotNone(xml_path, "FOMOD XML path was not found")
        self.assertTrue(os.path.exists(xml_path))

    def test_missing_data_files(self):
        """Test if common Morrowind data folders get automatically wrapped in a Data Files directory."""
        structure = {
            "SomeMod": {
                "textures": None,
                "meshes": None
            }
        }
        self.create_structure(structure)
        manager = FomodManager(self.test_dir, self.output_dir)
        manager.run()

        xml_path = self.get_latest_xml_path()
        self.assertIsNotNone(xml_path, "FOMOD XML path was not found")
        self.assertTrue(os.path.exists(xml_path))

    def test_fomod_folder_ignored(self):
        """Ensure that the 'fomod' folder does not appear in the generated XML."""
        structure = {
            "fomod": {
                "info.xml": "<fomod/>",
                "ModuleConfig.xml": ""
            },
            "Data Files": {
                "textures": None
            }
        }
        self.create_structure(structure)
        manager = FomodManager(self.test_dir, self.output_dir)
        manager.run()

        xml_path = self.get_latest_xml_path()
        self.assertIsNotNone(xml_path, "FOMOD XML path was not found")
        self.assertTrue(os.path.exists(xml_path))

    def test_relative_paths(self):
        """Ensure relative paths are used in the XML instead of absolute paths."""
        structure = {
            "Data Files": {
                "textures": None
            }
        }
        self.create_structure(structure)
        manager = FomodManager(self.test_dir, self.output_dir)
        manager.run()

        xml_path = self.get_latest_xml_path()
        self.assertIsNotNone(xml_path, "FOMOD XML path was not found")

        with open(xml_path, "r") as f:
            xml_content = f.read()

        self.assertNotIn(self.test_dir, xml_content)
        self.assertIn("Data Files", xml_content)


if __name__ == "__main__":
    unittest.main()
