"""
Reference Library - Load and lookup reference data
"""

import json
from pathlib import Path

class ReferenceLibrary:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.script_dir = Path(__file__).parent.parent
        self.ref_dir = self.script_dir / 'reference_data'
        
        # Loaded data
        self.creature_library = {}
        self.npc_library = {}
        self.weapons_reference = {}
        self.accessories_reference = {}
        self.armor_reference = {}
        self.herbs_reference = {}
        self.food_reference = {}
        self.transport_reference = {}
        
        # Stats
        self.stats = {
            'creatures': 0,
            'npcs': 0,
            'weapons': 0,
            'items': 0
        }
    
    def load_json(self, filename):
        """Load a JSON reference file"""
        filepath = self.ref_dir / filename
        if not filepath.exists():
            if self.verbose:
                print(f"  [WARN] {filename} not found (optional)")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ERROR loading {filename}: {e}")
            return None
    
    def load_creature_library(self):
        """Load creature/NPC library"""
        data = self.load_json('creature_npc_library.json')
        if data:
            self.creature_library = data.get('creatures', {})
            self.npc_library = data.get('npcs', {})
            self.stats['creatures'] = len(self.creature_library)
            self.stats['npcs'] = len(self.npc_library)
            print(f"  [OK] creature_npc_library.json: {self.stats['creatures']} creatures, {self.stats['npcs']} NPCs")
            return True
        else:
            print(f"  [WARN] No creature library - all NPCs must be custom")
            return False
    
    def load_weapons_reference(self):
        """Load Arms Law weapons"""
        data = self.load_json('arms_law_weapons.json')
        if data:
            weapons = data.get('weapons', [])
            self.weapons_reference = {w['name']: w for w in weapons}
            self.stats['weapons'] = len(self.weapons_reference)
            print(f"  [OK] arms_law_weapons.json: {self.stats['weapons']} weapons")
            return True
        else:
            print(f"  [WARN] No weapons reference - custom weapons need attack tables")
            return False
    
    def load_item_references(self):
        """Load Character Law item references"""
        loaded_count = 0
        
        # Accessories
        data = self.load_json('character_law_accessories.json')
        if data:
            items = data.get('items', [])
            self.accessories_reference = {item['name']: item for item in items}
            loaded_count += len(self.accessories_reference)
        
        # Armor - skip for now (different structure)
        # data = self.load_json('character_law_armor.json')
        # if data:
        #     armors = data.get('armor', [])
        #     self.armor_reference = {armor['type']: armor for armor in armors}
        #     loaded_count += len(self.armor_reference)
        
        # Herbs
        data = self.load_json('character_law_herbs.json')
        if data:
            herbs = data.get('herbs', [])
            self.herbs_reference = {herb['name']: herb for herb in herbs}
            loaded_count += len(self.herbs_reference)
        
        # Food
        data = self.load_json('character_law_food.json')
        if data:
            food = data.get('food', [])
            self.food_reference = {item['name']: item for item in food}
            loaded_count += len(self.food_reference)
        
        # Transport
        data = self.load_json('character_law_transport.json')
        if data:
            transport = data.get('transport', [])
            self.transport_reference = {item['name']: item for item in transport}
            loaded_count += len(self.transport_reference)
        
        self.stats['items'] = loaded_count
        if loaded_count > 0:
            print(f"  [OK] Character Law items: {loaded_count} items")
        return loaded_count > 0
    
    def load_all(self):
        """Load all reference files"""
        success = True
        
        # Creature library (important)
        if not self.load_creature_library():
            success = False
        
        # Weapons (important)
        if not self.load_weapons_reference():
            success = False
        
        # Items (less critical)
        self.load_item_references()
        
        return success
    
    def get_creature(self, name):
        """Get creature data by name"""
        if name in self.creature_library:
            return self.creature_library[name]
        if name in self.npc_library:
            return self.npc_library[name]
        return None
    
    def creature_exists(self, name):
        """Check if creature exists in library"""
        return name in self.creature_library or name in self.npc_library
    
    def get_weapon(self, name):
        """Get weapon data by name"""
        return self.weapons_reference.get(name)
    
    def weapon_exists(self, name):
        """Check if weapon exists in reference"""
        return name in self.weapons_reference
    
    def get_item(self, name):
        """Get item data by name (from any item reference)"""
        if name in self.accessories_reference:
            return self.accessories_reference[name]
        if name in self.armor_reference:
            return self.armor_reference[name]
        if name in self.herbs_reference:
            return self.herbs_reference[name]
        if name in self.food_reference:
            return self.food_reference[name]
        if name in self.transport_reference:
            return self.transport_reference[name]
        return None
    
    def item_exists(self, name):
        """Check if item exists in any reference"""
        return (name in self.accessories_reference or
                name in self.armor_reference or
                name in self.herbs_reference or
                name in self.food_reference or
                name in self.transport_reference)
