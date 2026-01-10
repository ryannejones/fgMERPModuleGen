"""
Module Loader - Load YAML files from module directory
"""

import yaml
from pathlib import Path

class ModuleLoader:
    def __init__(self, module_dir, verbose=False):
        self.module_dir = Path(module_dir)
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        
        # Module data
        self.config = {}
        self.stories = []
        self.encounters = []
        self.npcs = []
        self.items = []
        self.parcels = []
        self.images = []
        
        # Name to ID mappings (assigned during validation)
        self.name_to_id = {
            'story': {},
            'encounter': {},
            'npc': {},
            'item': {},
            'parcel': {},
            'image': {}
        }
    
    def log_error(self, message):
        """Log an error"""
        self.errors.append(message)
        if self.verbose:
            print(f"  ERROR: {message}")
    
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(message)
        if self.verbose:
            print(f"  WARNING: {message}")
    
    def load_yaml_file(self, filename):
        """Load a YAML file from module directory"""
        filepath = self.module_dir / filename
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.log_error(f"YAML syntax error in {filename}: {e}")
            return None
        except Exception as e:
            self.log_error(f"Failed to load {filename}: {e}")
            return None
    
    def load_module_config(self):
        """Load module.yaml (required)"""
        config = self.load_yaml_file('module.yaml')
        if not config:
            self.log_error("module.yaml is required but not found")
            return False
        
        # Validate required fields
        required = ['name', 'display_name', 'author']
        for field in required:
            if field not in config:
                self.log_error(f"module.yaml missing required field: {field}")
                return False
        
        # Validate name format (lowercase, no spaces)
        if not config['name'].islower() or ' ' in config['name']:
            self.log_error(f"module.yaml 'name' must be lowercase with no spaces: {config['name']}")
            return False
        
        self.config = config
        print(f"  [OK] module.yaml: {config['display_name']}")
        return True
    
    def load_stories(self):
        """Load stories.yaml (optional)"""
        data = self.load_yaml_file('stories.yaml')
        if data and 'stories' in data:
            self.stories = data['stories']
            print(f"  [OK] stories.yaml: {len(self.stories)} entries")
            return True
        return False
    
    def load_encounters(self):
        """Load encounters.yaml (optional)"""
        data = self.load_yaml_file('encounters.yaml')
        if data and 'encounters' in data:
            self.encounters = data['encounters']
            print(f"  [OK] encounters.yaml: {len(self.encounters)} encounters")
            return True
        return False
    
    def load_npcs(self):
        """Load npcs.yaml (optional)"""
        data = self.load_yaml_file('npcs.yaml')
        if data and 'npcs' in data:
            self.npcs = data['npcs']
            print(f"  [OK] npcs.yaml: {len(self.npcs)} custom NPCs")
            return True
        return False
    
    def load_items(self):
        """Load items.yaml (optional)"""
        data = self.load_yaml_file('items.yaml')
        if data and 'items' in data:
            self.items = data['items']
            print(f"  [OK] items.yaml: {len(self.items)} items")
            return True
        return False
    
    def load_parcels(self):
        """Load parcels.yaml (optional)"""
        data = self.load_yaml_file('parcels.yaml')
        if data and 'parcels' in data:
            self.parcels = data['parcels']
            print(f"  [OK] parcels.yaml: {len(self.parcels)} parcels")
            return True
        return False
    
    def load_images(self):
        """Load images.yaml (optional)"""
        data = self.load_yaml_file('images.yaml')
        if data and 'images' in data:
            self.images = data['images']
            print(f"  [OK] images.yaml: {len(self.images)} images")
            return True
        return False
    
    def load_all(self):
        """Load all module files"""
        # module.yaml is required
        if not self.load_module_config():
            return False
        
        # All others are optional
        self.load_stories()
        self.load_encounters()
        self.load_npcs()
        self.load_items()
        self.load_parcels()
        self.load_images()
        
        # Check if at least some content exists
        has_content = (
            len(self.stories) > 0 or
            len(self.encounters) > 0 or
            len(self.npcs) > 0 or
            len(self.items) > 0 or
            len(self.parcels) > 0 or
            len(self.images) > 0
        )
        
        if not has_content:
            self.log_warning("No content files found (module will be empty)")
        
        return True
    
    def print_errors(self):
        """Print all errors"""
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  • {error}")
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
