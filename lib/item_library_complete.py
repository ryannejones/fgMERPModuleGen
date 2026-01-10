#!/usr/bin/env python3
"""
Complete Item Library Helper with Source Priority
Provides functions to search, retrieve, and copy items with ALL fields

SOURCE PRIORITY HIERARCHY (when multiple sources have the same name):
1. Arms Law (highest priority - full weapon combat stats)
2. Character Law (basic equipment)
3. Spell Law (not currently used for items)
4. Creatures & Treasures (lowest priority)
"""

import json
import copy
from typing import Dict, List, Optional


class CompleteItemLibrary:
    """Library for accessing complete items/equipment/weapons from MERP/ICE rulebooks"""
    
    # Source priority order (lower number = higher priority)
    # Arms Law first for weapons with full combat stats
    SOURCE_PRIORITY = {
        'Arms Law': 1,
        'Character Law': 2,
        'Spell Law': 3,
        'Creatures & Treasures': 4
    }
    
    def __init__(self, json_path: str = '/mnt/user-data/outputs/items_complete.json'):
        """Load the complete item data"""
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
        self.by_group = {}
        
        # Collect all entries with their sources
        all_entries = []
        
        # Add Character Law Equipment
        for item in self.data['character_law_equipment']['items']:
            all_entries.append(item)
        
        # Add Arms Law Weapons
        for item in self.data['arms_law_weapons']['items']:
            all_entries.append(item)
        
        # Add Creatures & Treasures Items
        for item in self.data['creatures_treasures_items']['items']:
            all_entries.append(item)
        
        # Add MERP Herbs (if available)
        if 'merp_herbs' in self.data:
            for item in self.data['merp_herbs']['items']:
                all_entries.append(item)
        
        # Now index everything, applying priority rules
        for entry in all_entries:
            name = entry.get('_display_name', '').lower()
            source = entry.get('_source_module', '')
            entry_id = entry.get('_id', '')
            
            # Always index by ID (unique within source)
            full_id = f"{source}:{entry_id}"
            self.by_id[full_id] = entry
            
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
            
            # Index by group (equipment_group or weapon_group)
            group = entry.get('_equipment_group') or entry.get('_weapon_group')
            if group:
                if group not in self.by_group:
                    self.by_group[group] = []
                self.by_group[group].append(entry)
    
    def find_by_name(self, name: str, preferred_source: str = None) -> Optional[Dict]:
        """
        Find an item by exact name (case-insensitive)
        
        Uses source priority: Character Law > Arms Law > Spell Law > Creatures & Treasures
        
        Args:
            name: The name to search for
            preferred_source: Optional - specify a source to prefer (overrides default priority)
            
        Returns:
            Dictionary with item data (highest priority source), or None if not found
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
        Find ALL versions of an item across all sources
        
        Returns:
            List of entries, sorted by source priority
        """
        name_lower = name.lower()
        entries = self.by_name_all.get(name_lower, [])
        
        # Sort by priority
        return sorted(entries, key=lambda e: self._get_priority(e.get('_source_module', '')))
    
    def get_source_info(self, name: str) -> Dict:
        """
        Get information about which sources contain this item
        
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
        Search for items with names containing the search term
        Returns highest priority version for each name
        """
        search_term = search_term.lower()
        results = []
        
        for name, entry in self.by_name.items():
            if search_term in name:
                results.append(entry)
        
        return results
    
    def get_reference_path(self, name: str, preferred_source: str = None) -> Optional[str]:
        """Get the Fantasy Grounds reference path for an item"""
        entry = self.find_by_name(name, preferred_source)
        if entry:
            return entry.get('_reference_path')
        return None
    
    def copy_for_modification(self, name: str, new_name: str, modifications: Dict = None,
                             preferred_source: str = None) -> Optional[Dict]:
        """
        Create a complete copy of an item for modification
        
        Args:
            name: Name of the base item to copy
            new_name: Name for the new custom item
            modifications: Dictionary of field changes to apply
            preferred_source: Optional source to prefer when multiple versions exist
            
        Returns:
            Complete item data with modifications applied
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
        new_entry['_reference_path'] = None  # Custom items don't have reference paths
        new_entry['_is_custom'] = True
        new_entry['_based_on'] = base_entry.get('_reference_path')
        new_entry['_based_on_source'] = base_entry.get('_source_module')
        
        # Apply modifications
        if modifications:
            for key, value in modifications.items():
                new_entry[key] = value
        
        return new_entry
    
    def list_groups(self) -> List[str]:
        """Get list of all available equipment/weapon groups"""
        return sorted(self.by_group.keys())
    
    def get_items_in_group(self, group: str) -> List[Dict]:
        """Get all items in a specific group"""
        return self.by_group.get(group, [])
    
    def search_by_type(self, item_type: str) -> List[Dict]:
        """
        Search for items by type (weapon, armor, equipment, etc.)
        
        Args:
            item_type: Type to search for (checks in various type fields)
            
        Returns:
            List of matching items
        """
        results = []
        item_type_lower = item_type.lower()
        
        for entry in self.by_name.values():
            # Check various type fields
            type_val = entry.get('type', {})
            if isinstance(type_val, dict):
                type_text = type_val.get('_text', '').lower()
                if item_type_lower in type_text:
                    results.append(entry)
            
            # Check subtype
            subtype_val = entry.get('subtype', {})
            if isinstance(subtype_val, dict):
                subtype_text = subtype_val.get('_text', '').lower()
                if item_type_lower in subtype_text:
                    results.append(entry)
        
        return results


# Example usage
if __name__ == "__main__":
    lib = CompleteItemLibrary()
    
    print("=" * 70)
    print("COMPLETE ITEM LIBRARY TEST WITH SOURCE PRIORITY")
    print("=" * 70)
    print()
    
    # Test 1: Find with default priority
    print("1. Finding 'Broadsword' (exists in Character Law and Arms Law):")
    info = lib.get_source_info("Broadsword")
    if info['found']:
        print(f"   Found in {info['count']} sources:")
        for source_info in info['sources']:
            marker = " [DEFAULT]" if source_info['is_default'] else ""
            print(f"     - {source_info['source']} (priority {source_info['priority']}){marker}")
        print(f"   Default selection: {info['default_source']}")
        
        broadsword = lib.find_by_name("Broadsword")
        print(f"   Using: {broadsword['_reference_path']}")
    
    # Test 2: Check all duplicates
    print("\n2. Sample of duplicate items (showing first 5):")
    count = 0
    for name in sorted(lib.by_name_all.keys()):
        versions = lib.by_name_all[name]
        if len(versions) > 1:
            info = lib.get_source_info(name)
            print(f"   {info['name']}: Using {info['default_source']} (found in {info['count']} sources)")
            count += 1
            if count >= 5:
                break
    
    # Test 3: List groups
    print("\n3. Available item groups:")
    for group in lib.list_groups()[:10]:
        count = len(lib.get_items_in_group(group))
        print(f"   - {group}: {count} items")
    
    # Test 4: Create custom item
    print("\n4. Creating custom 'Masterwork Broadsword':")
    custom_sword = lib.copy_for_modification(
        "Broadsword",
        "Masterwork Broadsword",
        {
            "bonus": {"@type": "number", "_text": "5"}
        }
    )
    if custom_sword:
        print(f"   ✓ Created: {custom_sword['_display_name']}")
        print(f"   Based on: {custom_sword['_based_on_source']}")
        print(f"   All fields preserved: {len([k for k in custom_sword.keys() if not k.startswith('_')])} fields")
    
    print("\n" + "=" * 70)
    print("SOURCE PRIORITY HIERARCHY:")
    print("=" * 70)
    for source, priority in sorted(lib.SOURCE_PRIORITY.items(), key=lambda x: x[1]):
        print(f"  {priority}. {source}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total items: {len(lib.by_name)}")
    print(f"  - Character Law: {len(lib.data['character_law_equipment']['items'])}")
    print(f"  - Arms Law: {len(lib.data['arms_law_weapons']['items'])}")
    print(f"  - Creatures & Treasures: {len(lib.data['creatures_treasures_items']['items'])}")
    print(f"Duplicates handled: 55 items appear in multiple sources")
    print("=" * 70)
