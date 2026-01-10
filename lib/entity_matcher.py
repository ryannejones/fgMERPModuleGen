#!/usr/bin/env python3
"""
NPC/Creature/Item Matching System

Handles name resolution with multiple strategies:
1. Exact match in library
2. Check mapping file for aliases
3. Fuzzy matching with reasonable limits
4. Graceful failure with suggestions
"""

import yaml
from typing import Optional, Dict, List, Tuple
from difflib import SequenceMatcher


class EntityMatcher:
    """Matches user-provided names to library entries"""
    
    DEFAULT_LEVEL = 5  # Default for leveled NPCs when not specified (level 4 doesn't exist, 5 is closest mid-range)
    FUZZY_THRESHOLD = 0.80  # 80% similarity required for fuzzy match
    
    def __init__(self, 
                 npc_library,
                 item_library,
                 mapping_file: str = '/mnt/user-data/outputs/npc_creature_item_mappings.yaml'):
        """
        Initialize matcher with libraries and mappings
        
        Args:
            npc_library: Instance of CompleteNPCCreatureLibrary
            item_library: Instance of CompleteItemLibrary
            mapping_file: Path to YAML mapping file
        """
        self.npc_lib = npc_library
        self.item_lib = item_library
        
        # Load mappings
        with open(mapping_file, 'r') as f:
            self.mappings = yaml.safe_load(f)
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _find_fuzzy_matches(self, name: str, candidates: List[str], 
                           threshold: float = None) -> List[Tuple[str, float]]:
        """
        Find fuzzy matches above threshold
        
        Returns:
            List of (candidate, similarity_score) tuples, sorted by score
        """
        if threshold is None:
            threshold = self.FUZZY_THRESHOLD
        
        matches = []
        for candidate in candidates:
            score = self._similarity(name, candidate)
            if score >= threshold:
                matches.append((candidate, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def match_npc(self, name: str, level: Optional[int] = None) -> Dict:
        """
        Match an NPC/creature name to a library entry
        
        Args:
            name: NPC/creature name from user
            level: Optional level (uses DEFAULT_LEVEL if needed and not provided)
            
        Returns:
            Dictionary with:
                - 'found': bool
                - 'entry': NPC data dict (if found)
                - 'method': str (exact, mapped, fuzzy, or none)
                - 'original_name': str (what user requested)
                - 'matched_name': str (what was found)
                - 'suggestions': List[str] (if not found)
                - 'level_used': int (what level was used)
        """
        result = {
            'found': False,
            'entry': None,
            'method': 'none',
            'original_name': name,
            'matched_name': None,
            'suggestions': [],
            'level_used': level
        }
        
        # Strategy 1: Exact match
        entry = self.npc_lib.find_by_name(name)
        if entry:
            result['found'] = True
            result['entry'] = entry
            result['method'] = 'exact'
            result['matched_name'] = entry.get('_display_name', name)
            return result
        
        # Strategy 2: Check profession mappings
        if name in self.mappings.get('professions', {}):
            template_name = self.mappings['professions'][name]
            
            # Determine level to use
            if level is None:
                level = self.DEFAULT_LEVEL
                result['level_used'] = level
            
            # Find the template at this level
            entry = self.npc_lib.find_by_profession_and_level(template_name, level)
            if entry:
                result['found'] = True
                result['entry'] = entry
                result['method'] = 'mapped_profession'
                result['matched_name'] = f"{template_name} Level {level:02d}"  # Zero-pad to 2 digits
                return result
        
        # Strategy 3: Check creature aliases
        if name in self.mappings.get('creatures', {}):
            alias_target = self.mappings['creatures'][name]
            entry = self.npc_lib.find_by_name(alias_target)
            if entry:
                result['found'] = True
                result['entry'] = entry
                result['method'] = 'mapped_alias'
                result['matched_name'] = entry.get('_display_name', alias_target)
                return result
        
        # Strategy 4: Check generic NPC types
        if name in self.mappings.get('generic_npcs', {}):
            template_name = self.mappings['generic_npcs'][name]
            
            # Determine level
            if level is None:
                level = self.DEFAULT_LEVEL
                result['level_used'] = level
            
            # Try to find as profession first
            entry = self.npc_lib.find_by_profession_and_level(template_name, level)
            if not entry:
                # Maybe it's a direct name
                entry = self.npc_lib.find_by_name(template_name)
            
            if entry:
                result['found'] = True
                result['entry'] = entry
                result['method'] = 'mapped_generic'
                result['matched_name'] = entry.get('_display_name', template_name)
                return result
        
        # Strategy 5: Fuzzy matching
        all_names = list(self.npc_lib.by_name.keys())
        fuzzy_matches = self._find_fuzzy_matches(name, all_names)
        
        if fuzzy_matches:
            # Take best match
            best_match_name, score = fuzzy_matches[0]
            entry = self.npc_lib.find_by_name(best_match_name)
            
            if entry and score >= 0.90:  # Very high confidence
                result['found'] = True
                result['entry'] = entry
                result['method'] = 'fuzzy'
                result['matched_name'] = entry.get('_display_name', best_match_name)
                result['fuzzy_score'] = score
                return result
            
            # Lower confidence - provide as suggestions
            result['suggestions'] = [match[0] for match in fuzzy_matches[:5]]
        
        return result
    
    def match_item(self, name: str) -> Dict:
        """
        Match an item name to a library entry
        
        Args:
            name: Item name from user
            
        Returns:
            Dictionary with matching info (similar to match_npc)
        """
        result = {
            'found': False,
            'entry': None,
            'method': 'none',
            'original_name': name,
            'matched_name': None,
            'suggestions': []
        }
        
        # Strategy 1: Exact match
        entry = self.item_lib.find_by_name(name)
        if entry:
            result['found'] = True
            result['entry'] = entry
            result['method'] = 'exact'
            result['matched_name'] = entry.get('_display_name', name)
            return result
        
        # Strategy 2: Check item aliases
        if name in self.mappings.get('items', {}):
            alias_target = self.mappings['items'][name]
            entry = self.item_lib.find_by_name(alias_target)
            if entry:
                result['found'] = True
                result['entry'] = entry
                result['method'] = 'mapped_alias'
                result['matched_name'] = entry.get('_display_name', alias_target)
                return result
        
        # Strategy 3: Fuzzy matching
        all_names = list(self.item_lib.by_name.keys())
        fuzzy_matches = self._find_fuzzy_matches(name, all_names)
        
        if fuzzy_matches:
            best_match_name, score = fuzzy_matches[0]
            entry = self.item_lib.find_by_name(best_match_name)
            
            if entry and score >= 0.90:
                result['found'] = True
                result['entry'] = entry
                result['method'] = 'fuzzy'
                result['matched_name'] = entry.get('_display_name', best_match_name)
                result['fuzzy_score'] = score
                return result
            
            result['suggestions'] = [match[0] for match in fuzzy_matches[:5]]
        
        return result
    
    def create_custom_npc(self, name: str, based_on: str, level: Optional[int] = None,
                         modifications: Dict = None) -> Dict:
        """
        Create a custom NPC based on a template
        
        Args:
            name: Name for custom NPC
            based_on: Template to base it on (will be matched)
            level: Level for template (if applicable)
            modifications: Dictionary of field modifications
            
        Returns:
            Dictionary with custom NPC data or error info
        """
        # Match the base template
        base_match = self.match_npc(based_on, level)
        
        if not base_match['found']:
            return {
                'success': False,
                'error': f"Could not find base template '{based_on}'",
                'suggestions': base_match.get('suggestions', [])
            }
        
        # Create custom NPC using library
        custom_npc = self.npc_lib.copy_for_modification(
            base_match['matched_name'],
            name,
            modifications
        )
        
        if custom_npc:
            return {
                'success': True,
                'entry': custom_npc,
                'based_on': base_match['matched_name'],
                'method': base_match['method']
            }
        else:
            return {
                'success': False,
                'error': f"Failed to create custom NPC from '{base_match['matched_name']}'"
            }
    
    def create_custom_item(self, name: str, based_on: str, 
                          modifications: Dict = None) -> Dict:
        """Create a custom item based on a template"""
        # Match the base template
        base_match = self.match_item(based_on)
        
        if not base_match['found']:
            return {
                'success': False,
                'error': f"Could not find base item '{based_on}'",
                'suggestions': base_match.get('suggestions', [])
            }
        
        # Create custom item
        custom_item = self.item_lib.copy_for_modification(
            base_match['matched_name'],
            name,
            modifications
        )
        
        if custom_item:
            return {
                'success': True,
                'entry': custom_item,
                'based_on': base_match['matched_name'],
                'method': base_match['method']
            }
        else:
            return {
                'success': False,
                'error': f"Failed to create custom item from '{base_match['matched_name']}'"
            }


# Example usage
if __name__ == "__main__":
    from npc_creature_library_complete import CompleteNPCCreatureLibrary
    from item_library_complete import CompleteItemLibrary
    
    # Initialize
    npc_lib = CompleteNPCCreatureLibrary()
    item_lib = CompleteItemLibrary()
    matcher = EntityMatcher(npc_lib, item_lib)
    
    print("=" * 70)
    print("ENTITY MATCHING SYSTEM TEST")
    print("=" * 70)
    print()
    
    # Test 1: Exact match
    print("1. Exact match - 'Wolf':")
    result = matcher.match_npc("Wolf")
    print(f"   Found: {result['found']}")
    print(f"   Method: {result['method']}")
    print(f"   Matched: {result['matched_name']}")
    
    # Test 2: Profession mapping
    print("\n2. Profession mapping - 'Animist' (no level specified):")
    result = matcher.match_npc("Animist")
    print(f"   Found: {result['found']}")
    print(f"   Method: {result['method']}")
    print(f"   Matched: {result['matched_name']}")
    print(f"   Level used: {result['level_used']}")
    
    # Test 3: Profession with level
    print("\n3. Profession mapping - 'Animist' at level 10:")
    result = matcher.match_npc("Animist", level=10)
    print(f"   Found: {result['found']}")
    print(f"   Method: {result['method']}")
    print(f"   Matched: {result['matched_name']}")
    
    # Test 4: Creature alias
    print("\n4. Creature alias - 'Warg':")
    result = matcher.match_npc("Warg")
    print(f"   Found: {result['found']}")
    print(f"   Method: {result['method']}")
    print(f"   Matched: {result['matched_name']}")
    
    # Test 5: Generic term
    print("\n5. Generic term - 'Scout':")
    result = matcher.match_npc("Scout")
    print(f"   Found: {result['found']}")
    print(f"   Method: {result['method']}")
    print(f"   Matched: {result['matched_name']}")
    print(f"   Level used: {result['level_used']}")
    
    # Test 6: Fuzzy match
    print("\n6. Fuzzy match - 'Wolfe' (typo):")
    result = matcher.match_npc("Wolfe")
    print(f"   Found: {result['found']}")
    if result['found']:
        print(f"   Method: {result['method']}")
        print(f"   Matched: {result['matched_name']}")
        print(f"   Score: {result.get('fuzzy_score', 'N/A')}")
    else:
        print(f"   Suggestions: {result['suggestions'][:3]}")
    
    # Test 7: Not found
    print("\n7. Not found - 'Dragon':")
    result = matcher.match_npc("Dragon")
    print(f"   Found: {result['found']}")
    if not result['found'] and result['suggestions']:
        print(f"   Suggestions: {result['suggestions'][:3]}")
    
    # Test 8: Custom NPC
    print("\n8. Custom NPC - 'Skauril' based on 'Warrior' level 15:")
    result = matcher.create_custom_npc(
        "Skauril",
        based_on="Warrior",
        level=15,
        modifications={
            "hits": {"@type": "number", "_text": "150"}
        }
    )
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Based on: {result['based_on']}")
        print(f"   Method: {result['method']}")
    
    # Test 9: Item matching
    print("\n9. Item match - 'Sword' (alias for Broadsword):")
    result = matcher.match_item("Sword")
    print(f"   Found: {result['found']}")
    print(f"   Method: {result['method']}")
    print(f"   Matched: {result['matched_name']}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
