#!/usr/bin/env python3
"""
Complete NPC and Creature Library Helper with Source Priority
Provides functions to search, retrieve, and copy NPCs/creatures with ALL fields

SOURCE PRIORITY HIERARCHY (when multiple sources have the same name):
1. Character Law (highest priority)
2. Arms Law
3. Spell Law (not currently used for NPCs/creatures)
4. Creatures & Treasures (lowest priority)
"""

import json
import copy
from typing import Dict, List, Optional


class CompleteNPCCreatureLibrary:
    """Library for accessing complete NPCs and creatures from MERP/ICE rulebooks"""
    
    # Source priority order (lower number = higher priority)
    SOURCE_PRIORITY = {
        'Character Law': 1,
        'Arms Law': 2,
        'Spell Law': 3,
        'Creatures & Treasures': 4
    }
    
    def __init__(self, json_path: str = '/mnt/user-data/outputs/npcs_and_creatures_complete.json'):
        """Load the complete NPC and creature data"""
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        # Build quick lookup indexes with priority
        self._build_indexes()
    
    def _get_priority(self, source: str) -> int:
        """Get priority value for a source (lower is better)"""
        return self.SOURCE_PRIORITY.get(source, 999)
    
    def _build_indexes(self):
        """Build indexes for fast lookups with source priority"""
        self.by_name = {}  # Will store highest priority version only
        self.by_name_all = {}  # Will store all versions
        self.by_id = {}
        self.by_profession = {}
        self.by_level = {}
        
        # Collect all entries with their sources
        all_entries = []
        
        # Add Character Law NPCs
        for npc in self.data['character_law_npcs']['npcs']:
            all_entries.append(npc)
        
        # Add Arms Law creatures
        for creature in self.data['arms_law_creatures']['creatures']:
            all_entries.append(creature)
        
        # Add Creatures & Treasures
        for creature in self.data['creatures_treasures']['creatures']:
            all_entries.append(creature)
        
        # Now index everything, applying priority rules
        for entry in all_entries:
            name = entry.get('_display_name', '').lower()
            source = entry.get('_source_module', '')
            entry_id = entry.get('_id', '')
            
            # Always index by ID (unique)
            if entry_id:
                self.by_id[entry_id] = entry
            
            # Index by name with priority
            if name:
                # Store all versions
                if name not in self.by_name_all:
                    self.by_name_all[name] = []
                self.by_name_all[name].append(entry)
                
                # Store only highest priority version in main index
                if name not in self.by_name:
                    self.by_name[name] = entry
                else:
                    # Check priority - replace if new entry has higher priority
                    existing_source = self.by_name[name].get('_source_module', '')
                    if self._get_priority(source) < self._get_priority(existing_source):
                        self.by_name[name] = entry
            
            # Index by profession (Character Law NPCs only)
            if 'profession' in entry and isinstance(entry['profession'], dict):
                prof = entry['profession'].get('_text', '')
                if prof:
                    if prof not in self.by_profession:
                        self.by_profession[prof] = []
                    self.by_profession[prof].append(entry)
            
            # Index by level
            if 'level' in entry and isinstance(entry['level'], dict):
                level_text = entry['level'].get('_text', '0')
                try:
                    level = int(level_text)
                    if level not in self.by_level:
                        self.by_level[level] = []
                    self.by_level[level].append(entry)
                except ValueError:
                    pass
    
    def find_by_name(self, name: str, preferred_source: str = None) -> Optional[Dict]:
        """
        Find an NPC or creature by exact name (case-insensitive)
        
        Uses source priority: Character Law > Arms Law > Spell Law > Creatures & Treasures
        
        Args:
            name: The name to search for
            preferred_source: Optional - specify a source to prefer (overrides default priority)
            
        Returns:
            Dictionary with NPC/creature data (highest priority source), or None if not found
        """
        name_lower = name.lower()
        
        if preferred_source:
            # User specified a preferred source
            all_versions = self.by_name_all.get(name_lower, [])
            for entry in all_versions:
                if entry.get('_source_module') == preferred_source:
                    return entry
            # If preferred not found, fall through to default priority
        
        # Return highest priority version
        return self.by_name.get(name_lower)
    
    def find_all_by_name(self, name: str) -> List[Dict]:
        """
        Find ALL versions of an NPC/creature across all sources
        
        Returns:
            List of entries, sorted by source priority
        """
        name_lower = name.lower()
        entries = self.by_name_all.get(name_lower, [])
        
        # Sort by priority
        return sorted(entries, key=lambda e: self._get_priority(e.get('_source_module', '')))
    
    def get_source_info(self, name: str) -> Dict:
        """
        Get information about which sources contain this NPC/creature
        
        Returns:
            Dictionary with source information and priority selection
        """
        name_lower = name.lower()
        all_versions = self.by_name_all.get(name_lower, [])
        
        if not all_versions:
            return {'found': False, 'sources': []}
        
        sources = []
        for entry in all_versions:
            source = entry.get('_source_module', 'Unknown')
            ref_path = entry.get('_reference_path', '')
            priority = self._get_priority(source)
            sources.append({
                'source': source,
                'reference_path': ref_path,
                'priority': priority,
                'is_default': (entry == self.by_name.get(name_lower))
            })
        
        # Sort by priority
        sources.sort(key=lambda s: s['priority'])
        
        return {
            'found': True,
            'name': all_versions[0].get('_display_name', name),
            'count': len(sources),
            'sources': sources,
            'default_source': sources[0]['source'],
            'default_reference': sources[0]['reference_path']
        }
    
    def search_by_name(self, search_term: str) -> List[Dict]:
        """
        Search for NPCs/creatures with names containing the search term
        Returns highest priority version for each name
        """
        search_term = search_term.lower()
        results = []
        
        for name, entry in self.by_name.items():
            if search_term in name:
                results.append(entry)
        
        return results
    
    def find_by_profession_and_level(self, profession: str, level: int) -> Optional[Dict]:
        """Find an NPC by profession and level (Character Law only)"""
        if profession not in self.by_profession:
            return None
        
        for npc in self.by_profession[profession]:
            if 'level' in npc and isinstance(npc['level'], dict):
                npc_level_text = npc['level'].get('_text', '0')
                try:
                    npc_level = int(npc_level_text)
                    if npc_level == level:
                        return npc
                except ValueError:
                    pass
        
        return None
    
    def get_reference_path(self, name: str, preferred_source: str = None) -> Optional[str]:
        """Get the Fantasy Grounds reference path for an NPC/creature"""
        entry = self.find_by_name(name, preferred_source)
        if entry:
            return entry.get('_reference_path')
        return None
    
    def copy_for_modification(self, name: str, new_name: str, modifications: Dict = None,
                             preferred_source: str = None) -> Optional[Dict]:
        """
        Create a complete copy of an NPC/creature for modification
        
        Args:
            name: Name of the base NPC/creature to copy
            new_name: Name for the new custom NPC/creature
            modifications: Dictionary of field changes to apply
            preferred_source: Optional source to prefer when multiple versions exist
            
        Returns:
            Complete NPC/creature data with modifications applied
        """
        base_entry = self.find_by_name(name, preferred_source)
        if not base_entry:
            return None
        
        # Deep copy to avoid modifying original
        new_entry = copy.deepcopy(base_entry)
        
        # Update the name
        if 'name' in new_entry and isinstance(new_entry['name'], dict):
            new_entry['name']['_text'] = new_name
        if 'nonid_name' in new_entry and isinstance(new_entry['nonid_name'], dict):
            new_entry['nonid_name']['_text'] = new_name
        
        # Update metadata
        new_entry['_display_name'] = new_name
        new_entry['_id'] = f"id-custom-{new_name.lower().replace(' ', '_')}"
        new_entry['_reference_path'] = None  # Custom NPCs don't have reference paths
        new_entry['_is_custom'] = True
        new_entry['_based_on'] = base_entry.get('_display_name')  # Store the display name for weapon assignment
        new_entry['_based_on_path'] = base_entry.get('_reference_path')  # Store original reference path
        new_entry['_based_on_source'] = base_entry.get('_source_module')
        
        # Apply modifications
        if modifications:
            # Field type mappings for proper FG XML conversion
            number_fields = {'hp', 'at', 'db', 'level', 'baserate', 'reach', 'outlook'}
            string_fields = {'profession', 'race', 'group', 'subgroup', 'abilities', 
                           'description', 'spells', 'stats', 'size'}
            
            for key, value in modifications.items():
                # If the field already exists in the NPC, preserve its structure
                if key in new_entry and isinstance(new_entry[key], dict):
                    # Update only the _text value, preserving @type and other attributes
                    if '_text' in new_entry[key]:
                        new_entry[key]['_text'] = str(value)
                    else:
                        # Fallback: replace entirely with proper structure
                        if key in number_fields:
                            new_entry[key] = {'@type': 'number', '_text': str(value)}
                        elif key in string_fields:
                            new_entry[key] = {'@type': 'string', '_text': str(value)}
                        else:
                            # Unknown field - try to preserve type if possible
                            field_type = new_entry[key].get('@type', 'string')
                            new_entry[key] = {'@type': field_type, '_text': str(value)}
                else:
                    # Field doesn't exist - create new field with proper structure
                    if key in number_fields:
                        new_entry[key] = {'@type': 'number', '_text': str(value)}
                    elif key in string_fields:
                        new_entry[key] = {'@type': 'string', '_text': str(value)}
                    else:
                        # For unknown fields, assume string type
                        new_entry[key] = {'@type': 'string', '_text': str(value)}
        
        return new_entry
    
    def list_professions(self) -> List[str]:
        """Get list of all available professions"""
        return sorted(self.by_profession.keys())
    
    def list_levels_for_profession(self, profession: str) -> List[int]:
        """Get list of available levels for a profession"""
        if profession not in self.by_profession:
            return []
        
        levels = []
        for npc in self.by_profession[profession]:
            if 'level' in npc and isinstance(npc['level'], dict):
                level_text = npc['level'].get('_text', '0')
                try:
                    levels.append(int(level_text))
                except ValueError:
                    pass
        
        return sorted(set(levels))
    
    def get_all_at_level(self, level: int) -> List[Dict]:
        """Get all NPCs/creatures at a specific level"""
        return self.by_level.get(level, [])
    
    def search_creatures_by_group(self, group: str) -> List[Dict]:
        """Search for creatures by group (e.g., "Animals", "Monsters")"""
        results = []
        seen_names = set()
        
        # Collect all matches, but only keep highest priority version of each name
        for entry in self.by_name.values():
            if 'group' in entry and isinstance(entry['group'], dict):
                creature_group = entry['group'].get('_text', '').lower()
                if creature_group == group.lower():
                    name = entry.get('_display_name', '').lower()
                    if name not in seen_names:
                        results.append(entry)
                        seen_names.add(name)
        
        return results
    
    def get_simple_stats(self, name: str, preferred_source: str = None) -> Optional[Dict]:
        """Get simplified stats for quick reference"""
        entry = self.find_by_name(name, preferred_source)
        if not entry:
            return None
        
        def get_text_value(field_dict, default=''):
            if isinstance(field_dict, dict):
                return field_dict.get('_text', default)
            return default
        
        stats = {
            'name': entry.get('_display_name', ''),
            'id': entry.get('_id', ''),
            'source': entry.get('_source_module', ''),
            'reference_path': entry.get('_reference_path', '')
        }
        
        # Extract common fields
        for field in ['level', 'hits', 'db', 'at']:
            if field in entry and isinstance(entry[field], dict):
                try:
                    stats[field] = int(get_text_value(entry[field], '0'))
                except ValueError:
                    stats[field] = get_text_value(entry[field], '0')
        
        return stats


# Example usage
if __name__ == "__main__":
    lib = CompleteNPCCreatureLibrary()
    
    print("=" * 70)
    print("COMPLETE NPC/CREATURE LIBRARY TEST WITH SOURCE PRIORITY")
    print("=" * 70)
    print()
    
    # Test 1: Find with default priority
    print("1. Finding 'Basilisk' (exists in Arms Law and Creatures & Treasures):")
    info = lib.get_source_info("Basilisk")
    if info['found']:
        print(f"   Found in {info['count']} sources:")
        for source_info in info['sources']:
            marker = " [DEFAULT]" if source_info['is_default'] else ""
            print(f"     - {source_info['source']} (priority {source_info['priority']}){marker}")
        print(f"   Default selection: {info['default_source']}")
        
        # Get the default
        basilisk = lib.find_by_name("Basilisk")
        print(f"   Using: {basilisk['_reference_path']}")
    
    # Test 2: Prefer a specific source
    print("\n2. Finding 'Basilisk' with preferred source 'Creatures & Treasures':")
    basilisk_ct = lib.find_by_name("Basilisk", preferred_source="Creatures & Treasures")
    if basilisk_ct:
        print(f"   Using: {basilisk_ct['_reference_path']}")
    
    # Test 3: Get all versions
    print("\n3. Getting ALL versions of 'Orc':")
    all_orcs = lib.find_all_by_name("Orc (non-combatant)")
    for orc in all_orcs:
        print(f"   - {orc['_source_module']}: {orc['_reference_path']}")
    
    # Test 4: Show priority in action
    print("\n4. Testing priority with multiple duplicates:")
    test_names = ["Wolf", "Eagle", "Goblin"]
    for name in test_names:
        info = lib.get_source_info(name)
        if info['found']:
            print(f"   {name}: Using {info['default_source']} (found in {info['count']} sources)")
    
    # Test 5: Create custom based on highest priority
    print("\n5. Creating custom 'Elder Basilisk' (auto-selects Arms Law version):")
    elder = lib.copy_for_modification(
        "Basilisk",
        "Elder Basilisk",
        {
            "level": {"@type": "number", "_text": "10"},
            "hits": {"@type": "number", "_text": "150"}
        }
    )
    if elder:
        print(f"   ✓ Created: {elder['_display_name']}")
        print(f"   Based on: {elder['_based_on_source']}")
        print(f"   Reference: {elder['_based_on']}")
    
    print("\n" + "=" * 70)
    print("SOURCE PRIORITY HIERARCHY:")
    print("=" * 70)
    for source, priority in sorted(lib.SOURCE_PRIORITY.items(), key=lambda x: x[1]):
        print(f"  {priority}. {source}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
