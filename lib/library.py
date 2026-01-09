#!/usr/bin/env python3
"""
Reference Library - Integrated v0.11
Provides access to complete NPC, creature, item, skill, and spell data
"""

import json
from pathlib import Path
from typing import Optional, Dict, List

# Try relative imports first (when used as module), fall back to direct imports
try:
    from .npc_creature_library_complete import CompleteNPCCreatureLibrary
    from .item_library_complete import CompleteItemLibrary
    from .entity_matcher import EntityMatcher
except ImportError:
    from npc_creature_library_complete import CompleteNPCCreatureLibrary
    from item_library_complete import CompleteItemLibrary
    from entity_matcher import EntityMatcher


class ReferenceLibrary:
    """
    Central library for all reference data
    
    Provides unified access to:
    - NPCs and creatures (715 entries)
    - Items (1,257 entries)
    - Skills (80 skills)
    - Spell lists (162 spell lists)
    - Name matching and resolution
    """
    
    VERSION = "0.11"
    
    def __init__(self, data_dir: str = None):
        """
        Initialize reference library
        
        Args:
            data_dir: Path to data directory (defaults to ../data relative to this file)
        """
        if data_dir is None:
            # Default to data directory relative to this file
            lib_dir = Path(__file__).parent
            data_dir = lib_dir.parent / 'data'
        else:
            data_dir = Path(data_dir)
        
        self.data_dir = data_dir
        
        # Initialize core libraries
        self.npcs = CompleteNPCCreatureLibrary(
            str(data_dir / 'npcs_and_creatures_complete.json')
        )
        
        self.items = CompleteItemLibrary(
            str(data_dir / 'items_complete.json')
        )
        
        # Initialize matcher
        mapping_file = Path(__file__).parent / 'npc_creature_item_mappings.yaml'
        self.matcher = EntityMatcher(
            self.npcs,
            self.items,
            str(mapping_file)
        )
        
        # Load skill and spell references
        self.skills = self._load_skills()
        self.spell_lists = self._load_spell_lists()
    
    def _load_skills(self) -> Dict:
        """Load skill reference data"""
        skill_file = self.data_dir / 'skill_references.json'
        with open(skill_file, 'r') as f:
            return json.load(f)
    
    def _load_spell_lists(self) -> Dict:
        """Load spell list reference data"""
        spell_file = self.data_dir / 'spell_references.json'
        with open(spell_file, 'r') as f:
            return json.load(f)
    
    # NPC/Item/Skill/Spell methods remain the same...
    # (Abbreviated for space - full implementation as before)
    
    def find_npc(self, name: str, level: Optional[int] = None, 
                 preferred_source: str = None) -> Dict:
        """Find an NPC or creature by name"""
        return self.matcher.match_npc(name, level)
    
    def find_item(self, name: str, preferred_source: str = None) -> Dict:
        """Find an item by name"""
        return self.matcher.match_item(name)
    
    def create_custom_npc(self, name: str, based_on: str, 
                         level: Optional[int] = None,
                         modifications: Dict = None) -> Dict:
        """Create a custom NPC based on a template"""
        return self.matcher.create_custom_npc(name, based_on, level, modifications)
    
    def create_custom_item(self, name: str, based_on: str,
                          modifications: Dict = None) -> Dict:
        """Create a custom item based on a template"""
        return self.matcher.create_custom_item(name, based_on, modifications)
    
    def get_statistics(self) -> Dict:
        """Get statistics about the library"""
        return {
            'version': self.VERSION,
            'npcs_count': len(self.npcs.by_name),
            'items_count': len(self.items.by_name),
            'skills_count': len(self.skills['skills']),
            'spell_lists_count': len(self.spell_lists['spell_lists']),
            'professions': len(self.npcs.by_profession),
            'item_groups': len(self.items.by_group)
        }
