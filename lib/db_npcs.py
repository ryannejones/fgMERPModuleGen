"""
NPC XML Generator v0.11 - Generate <npc> section with item references
Uses references to module items (single point of truth)
When players loot, FG automatically copies full item data to character
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional


class NPCGenerator:
    """
    Generates NPC XML using complete stat blocks from the library
    
    Features:
    - NPCs use complete stat blocks from library
    - Weapons/equipment reference module item list
    - FG copies item data when looted by players
    """
    
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.next_id = 1
        
    def get_next_id(self):
        """Get next NPC ID"""
        npc_id = f"id-{self.next_id:05d}"
        self.next_id += 1
        return npc_id
    
    def dict_to_xml(self, data: Dict[str, Any], parent: ET.Element, 
                    skip_items: bool = False):
        """
        Recursively convert dictionary to XML
        
        Args:
            data: Dictionary to convert
            parent: Parent XML element
            skip_items: If True, skip weapon/item sections (handled separately)
        """
        for key, value in data.items():
            if key.startswith('_'):
                # Skip metadata fields
                continue
            
            # Skip weapon/item sections if we're handling them separately
            if skip_items and key in ['weapons', 'defences', 'items']:
                continue
            
            if key.startswith('@'):
                # This is an attribute
                attr_name = key[1:]
                parent.set(attr_name, str(value))
            
            elif isinstance(value, dict):
                if '_text' in value:
                    # Simple element with attributes and text
                    elem = ET.SubElement(parent, key)
                    elem.text = str(value['_text'])
                    # Add any attributes
                    for k, v in value.items():
                        if k.startswith('@'):
                            attr_name = k[1:]
                            elem.set(attr_name, str(v))
                else:
                    # Complex nested structure
                    elem = ET.SubElement(parent, key)
                    self.dict_to_xml(value, elem, skip_items)
            
            elif isinstance(value, list):
                # Multiple items with same tag
                for item in value:
                    elem = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        self.dict_to_xml(item, elem, skip_items)
                    else:
                        elem.text = str(item)
            
            else:
                # Simple value
                elem = ET.SubElement(parent, key)
                elem.text = str(value)
    
    def create_item_reference(self, item_name: str, parent: ET.Element, 
                            tag: str = "link") -> Optional[ET.Element]:
        """
        Create a reference to an item in the module's item list
        
        Args:
            item_name: Name of item to reference
            parent: Parent element to add link to
            tag: Tag name for the link element
            
        Returns:
            Link element or None if item not found
        """
        # Check if this item is in the module's item list
        if item_name not in self.loader.name_to_id.get('item', {}):
            if self.verbose:
                print(f"    Warning: Item '{item_name}' not in module item list")
            return None
        
        item_id = self.loader.name_to_id['item'][item_name]
        
        # Create link element
        link = ET.SubElement(parent, tag)
        link.set('type', 'windowreference')
        
        link_class = ET.SubElement(link, 'class')
        link_class.text = 'item'
        
        recordname = ET.SubElement(link, 'recordname')
        recordname.text = f'item.{item_id}'
        
        return link
    
    def add_weapons_with_references(self, npc_data: Dict, npc_elem: ET.Element):
        """
        Add weapon section with references to module items
        
        If weapon exists in module item list, creates reference
        Otherwise, embeds full weapon data
        """
        if 'weapons' not in npc_data:
            return
        
        weapons_section = ET.SubElement(npc_elem, 'weapons')
        weapons = npc_data['weapons']
        
        if not isinstance(weapons, dict):
            return
        
        for weapon_id, weapon_data in weapons.items():
            if weapon_id.startswith('_'):
                continue
            
            weapon_elem = ET.SubElement(weapons_section, weapon_id)
            
            if isinstance(weapon_data, dict):
                weapon_name = None
                if 'name' in weapon_data:
                    if isinstance(weapon_data['name'], dict):
                        weapon_name = weapon_data['name'].get('_text')
                    else:
                        weapon_name = weapon_data['name']
                
                # Try to create reference
                if weapon_name and weapon_name in self.loader.name_to_id.get('item', {}):
                    # Create reference to module item
                    self.create_item_reference(weapon_name, weapon_elem, 'link')
                    
                    # Add count if specified
                    if 'count' in weapon_data:
                        count = ET.SubElement(weapon_elem, 'count')
                        count.set('type', 'number')
                        if isinstance(weapon_data['count'], dict):
                            count.text = str(weapon_data['count'].get('_text', '1'))
                        else:
                            count.text = str(weapon_data['count'])
                else:
                    # Weapon not in module, embed full data
                    self.dict_to_xml(weapon_data, weapon_elem)
    
    def create_npc_from_library(self, npc_data: Dict, use_item_refs: bool = True) -> ET.Element:
        """
        Create NPC element from complete library data
        
        Note: The caller must assign the element's tag (ID) after creation
        
        Args:
            npc_data: Complete NPC dictionary from library
            use_item_refs: If True, use item references where possible
            
        Returns:
            XML Element with complete stat block (tag will be temporary)
        """
        # Create element with temporary tag (caller will set the real ID)
        npc_elem = ET.Element('temp')
        
        if use_item_refs:
            # Convert NPC data but skip weapon section
            self.dict_to_xml(npc_data, npc_elem, skip_items=True)
            
            # Add weapons with references
            self.add_weapons_with_references(npc_data, npc_elem)
        else:
            # Convert everything including embedded items
            self.dict_to_xml(npc_data, npc_elem, skip_items=False)
        
        return npc_elem
    
    def create_npc_from_yaml(self, yaml_npc: Dict) -> ET.Element:
        """
        Create NPC from YAML specification
        
        Handles three cases:
        1. Simple reference (just name) - Find in library
        2. Reference with level - Find profession-based NPC
        3. Custom NPC with 'based_on' - Copy template and modify
        
        Args:
            yaml_npc: NPC specification from YAML
            
        Returns:
            XML Element or None if not found
        """
        npc_name = yaml_npc.get('name')
        if not npc_name:
            print(f"  WARNING: NPC without name: {yaml_npc}")
            return None
        
        # Get next ID BEFORE creating
        npc_id = self.get_next_id()
        
        # Case 1 & 2: Find existing NPC
        if 'based_on' not in yaml_npc:
            level = yaml_npc.get('level')
            result = self.library.find_npc(npc_name, level)
            
            if not result['found']:
                print(f"  WARNING: NPC '{npc_name}' not found in library")
                if result.get('suggestions'):
                    print(f"    Suggestions: {', '.join(result['suggestions'][:3])}")
                return None
            
            if self.verbose:
                print(f"  Found '{npc_name}' via {result['method']}: {result['matched_name']}")
            
            # Store ID for cross-referencing BEFORE creating element
            self.loader.name_to_id['npc'][npc_name] = npc_id
            
            # Create XML from library data (with item references)
            npc_elem = self.create_npc_from_library(result['entry'], use_item_refs=True)
            # Update the element's tag to the assigned ID
            npc_elem.tag = npc_id
            return npc_elem
        
        # Case 3: Custom NPC based on template
        else:
            based_on = yaml_npc['based_on']
            level = yaml_npc.get('level')
            modifications = yaml_npc.get('modifications', {})
            
            result = self.library.create_custom_npc(
                npc_name,
                based_on,
                level,
                modifications
            )
            
            if not result['success']:
                print(f"  WARNING: Could not create custom NPC '{npc_name}'")
                print(f"    {result['error']}")
                if result.get('suggestions'):
                    print(f"    Suggestions: {', '.join(result['suggestions'][:3])}")
                return None
            
            if self.verbose:
                print(f"  Created custom '{npc_name}' based on {result['based_on']}")
            
            # Store ID for cross-referencing BEFORE creating element
            self.loader.name_to_id['npc'][npc_name] = npc_id
            
            # Create XML from custom data (with item references)
            npc_elem = self.create_npc_from_library(result['entry'], use_item_refs=True)
            # Update the element's tag to the assigned ID
            npc_elem.tag = npc_id
            return npc_elem
    
    def generate(self):
        """Generate the complete <npc> section"""
        if self.verbose:
            print(f"\nGenerating NPCs...")
        
        # Create root npc element
        npc_root = ET.Element('npc')
        
        # Track which NPCs we've already generated
        generated_npcs = {}  # name -> npc_id mapping
        
        # Step 1: Generate custom NPCs from npcs.yaml
        custom_count = 0
        if self.loader.npcs:
            if self.verbose:
                print(f"  Processing {len(self.loader.npcs)} custom NPCs from npcs.yaml...")
            
            for yaml_npc in self.loader.npcs:
                npc_elem = self.create_npc_from_yaml(yaml_npc)
                if npc_elem is not None:
                    npc_root.append(npc_elem)
                    custom_count += 1
                    # Track this NPC
                    npc_name = yaml_npc.get('name')
                    if npc_name:
                        generated_npcs[npc_name] = npc_elem.tag
        
        # Step 2: Collect unique NPCs from encounters
        encounter_npcs = {}  # name -> {level, based_on} mapping
        if self.loader.encounters:
            for encounter in self.loader.encounters:
                for npc_ref in encounter.get('npcs', []):
                    npc_name = npc_ref.get('creature') or npc_ref.get('name')
                    if npc_name and npc_name not in generated_npcs:
                        # Store unique NPC with its details
                        key = npc_name
                        if npc_ref.get('level'):
                            key = f"{npc_name}_L{npc_ref['level']}"
                        
                        if key not in encounter_npcs:
                            encounter_npcs[key] = {
                                'name': npc_name,
                                'level': npc_ref.get('level'),
                                'based_on': npc_ref.get('based_on')
                            }
        
        # Step 3: Generate NPCs from encounters
        encounter_count = 0
        if encounter_npcs:
            if self.verbose:
                print(f"  Processing {len(encounter_npcs)} unique NPCs from encounters...")
            
            for key, npc_info in encounter_npcs.items():
                npc_name = npc_info['name']
                level = npc_info['level']
                based_on = npc_info['based_on']
                
                # Create NPC specification
                yaml_npc = {'name': npc_name}
                if level:
                    yaml_npc['level'] = level
                if based_on:
                    yaml_npc['based_on'] = based_on
                
                # Generate the NPC
                npc_elem = self.create_npc_from_yaml(yaml_npc)
                if npc_elem is not None:
                    npc_root.append(npc_elem)
                    encounter_count += 1
                    # Track this NPC by original name for battle references
                    generated_npcs[npc_name] = npc_elem.tag
        
        if self.verbose:
            print(f"  [OK] Generated {custom_count} custom NPCs")
            print(f"  [OK] Generated {encounter_count} encounter NPCs")
            print(f"  [OK] Total: {custom_count + encounter_count} NPCs")
        
        if custom_count + encounter_count == 0:
            return None
        
        return npc_root
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
