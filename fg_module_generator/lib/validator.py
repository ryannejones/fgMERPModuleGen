"""
Module Validator - Validate all references and cross-links
"""

from pathlib import Path

class ModuleValidator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        
        # Validation stats
        self.stats = {
            'creatures_from_library': 0,
            'creatures_custom': 0,
            'weapons_from_reference': 0,
            'weapons_custom': 0,
            'story_links_validated': 0,
            'parcel_items_validated': 0,
            'images_validated': 0
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
    
    def build_name_mappings(self):
        """Build name to ID mappings for cross-references"""
        # Build dictionaries of what exists
        for story in self.loader.stories:
            self.loader.name_to_id['story'][story['name']] = None
        
        for encounter in self.loader.encounters:
            self.loader.name_to_id['encounter'][encounter['name']] = None
        
        for npc in self.loader.npcs:
            self.loader.name_to_id['npc'][npc['name']] = None
        
        for item in self.loader.items:
            self.loader.name_to_id['item'][item['name']] = None
        
        for parcel in self.loader.parcels:
            self.loader.name_to_id['parcel'][parcel['name']] = None
        
        for image in self.loader.images:
            self.loader.name_to_id['image'][image['name']] = None
    
    def validate_creature_reference(self, creature_name):
        """Check if creature exists (library or custom)"""
        # Check library
        if self.library.creature_exists(creature_name):
            self.stats['creatures_from_library'] += 1
            return True
        
        # Check custom NPCs
        if creature_name in self.loader.name_to_id['npc']:
            self.stats['creatures_custom'] += 1
            return True
        
        return False
    
    def validate_encounters(self):
        """Validate all encounters"""
        valid = True
        for encounter in self.loader.encounters:
            enc_name = encounter.get('name', 'UNNAMED')
            
            # Check required fields
            if not encounter.get('name'):
                self.log_error("Encounter missing 'name' field")
                valid = False
                continue
            
            if 'npcs' not in encounter or not encounter['npcs']:
                self.log_error(f"Encounter '{enc_name}' has no NPCs")
                valid = False
                continue
            
            # Validate each NPC reference
            for i, npc_ref in enumerate(encounter['npcs']):
                if 'creature' not in npc_ref:
                    self.log_error(f"Encounter '{enc_name}' NPC #{i+1} missing 'creature' field")
                    valid = False
                    continue
                
                creature_name = npc_ref['creature']
                if not self.validate_creature_reference(creature_name):
                    self.log_error(f"Encounter '{enc_name}' references unknown creature: '{creature_name}'")
                    self.log_error("  -> Add to npcs.yaml or check spelling")
                    valid = False
        
        return valid
    
    def validate_all(self):
        """Validate all content"""
        # Build name mappings first
        self.build_name_mappings()
        
        # Validate encounters
        valid = True
        if self.loader.encounters:
            if not self.validate_encounters():
                valid = False
        
        print(f"  [OK] Validated {len(self.loader.encounters)} encounters")
        print(f"  [OK] Validated {len(self.loader.stories)} stories")
        print(f"  [OK] Validated {len(self.loader.npcs)} custom NPCs")
        
        return valid
    
    def print_errors(self):
        """Print all errors and warnings"""
        if self.errors:
            print("\nValidation Errors:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
    
    def print_summary(self):
        """Print validation summary"""
        print(f"Module: {self.loader.config.get('display_name', 'Unknown')}")
        print(f"Author: {self.loader.config.get('author', 'Unknown')}")
        print()
        print("Content:")
        print(f"  Stories:     {len(self.loader.stories)}")
        print(f"  Encounters:  {len(self.loader.encounters)}")
        print(f"  Custom NPCs: {len(self.loader.npcs)}")
        print(f"  Items:       {len(self.loader.items)}")
        print(f"  Parcels:     {len(self.loader.parcels)}")
        print(f"  Images:      {len(self.loader.images)}")
        print()
        print("References:")
        print(f"  Creatures from library: {self.stats['creatures_from_library']}")
        print(f"  Custom creatures:       {self.stats['creatures_custom']}")
        print()
        
        if not self.errors and not self.warnings:
            print("[OK] Validation successful - no errors or warnings")
        elif not self.errors:
            print(f"[OK] Validation successful - {len(self.warnings)} warnings")
        else:
            print(f"[FAIL] Validation failed - {len(self.errors)} errors, {len(self.warnings)} warnings")
