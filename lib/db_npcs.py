"""
NPC XML Generator v0.12 - Generate <npc> section with item references and default weapons
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
        
        # Load default weapons mapping
        import yaml
        import os
        weapons_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'default_weapons.yaml')
        try:
            with open(weapons_path, 'r') as f:
                self.default_weapons = yaml.safe_load(f) or {}
        except FileNotFoundError:
            self.default_weapons = {}
            if self.verbose:
                print("  Warning: default_weapons.yaml not found, skipping weapon assignment")
 
    def _add_attacktable_from_item(self, weapon_elem: ET.Element, weapon_name: str) -> bool:
        """Copy attacktable onto npc.weapons.* from the generated item dict (loader.item_generator.created_items)."""

        # If an attacktable element exists but is empty, replace it
        existing = weapon_elem.find("attacktable")
        if existing is not None:
            tableid_node = existing.find("tableid")
            if tableid_node is not None and (tableid_node.text or "").strip():
                return True
            weapon_elem.remove(existing)

        def _txt(v):
            if isinstance(v, dict):
                return v.get("_text", "")
            return "" if v is None else str(v)

        item_gen = getattr(self.loader, "item_generator", None)
        if not item_gen or not hasattr(item_gen, "created_items"):
            return False

        item_dict = item_gen.created_items.get(weapon_name)
        if not isinstance(item_dict, dict):
            return False

        # Attack table may be top-level or nested
        atk = item_dict.get("attacktable")
        if not isinstance(atk, dict):
            weapon_block = item_dict.get("weapon")
            if isinstance(weapon_block, dict):
                atk = weapon_block.get("attacktable")

        if not isinstance(atk, dict):
            return False

        tableid = _txt(atk.get("tableid"))
        if not tableid:
            return False

        attacktable_elem = ET.SubElement(weapon_elem, "attacktable")

        name_elem = ET.SubElement(attacktable_elem, "name")
        name_elem.set("type", "string")
        name_elem.text = _txt(atk.get("name")) or weapon_name

        tableid_elem = ET.SubElement(attacktable_elem, "tableid")
        tableid_elem.set("type", "string")
        tableid_elem.text = tableid

        return True


    def ensure_auto_letter_token(self, npc_elem: ET.Element, npc_id: str, npc_display_name: str):
        """
        If no explicit token was added, assign a generated letter token.
        This makes encounter->map dragging work even without custom token art.
        """

        mod = self.loader.config["name"]
        
        # Don't override an existing token (e.g., from YAML tokens or file-based tokens)
        if npc_elem.find('token') is not None:
            return

        token_path = f"tokens/{npc_id}.png"

        token = ET.SubElement(npc_elem, 'token')
        token.set('type', 'token')
        token.text = token_path

        # Record this token so the packager can generate the PNG into the .mod
        if not hasattr(self.loader, 'generated_tokens'):
            self.loader.generated_tokens = {}

        name = (npc_display_name or "").strip()
        initial = name[:1].upper() if name else "?"
        self.loader.generated_tokens[token_path] = initial
    
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
                
                if self.verbose and weapon_name:
                    ob_val = weapon_data.get('ob', {})
                    if isinstance(ob_val, dict):
                        ob_val = ob_val.get('_text', 'N/A')
                    print(f"    DEBUG: Processing weapon {weapon_id}: {weapon_name}, OB in data: {ob_val}")
                
                # Try to create reference
                if weapon_name and weapon_name in self.loader.name_to_id.get('item', {}):
                    # Create reference to module item
                    self.create_item_reference(weapon_name, weapon_elem, 'link')
                    
                    # FG weapons need name and OB alongside the link
                    if 'name' in weapon_data:
                        name_elem = ET.SubElement(weapon_elem, 'name')
                        name_elem.set('type', 'string')
                        if isinstance(weapon_data['name'], dict):
                            name_elem.text = weapon_data['name'].get('_text', weapon_name)
                        else:
                            name_elem.text = weapon_data['name']
                    
                    if 'ob' in weapon_data:
                        try:
                            ob_elem = ET.SubElement(weapon_elem, 'ob')
                            ob_elem.set('type', 'number')
                            ob_val = weapon_data['ob']
                            if isinstance(ob_val, dict):
                                ob_text = str(ob_val.get('_text', '0'))
                            else:
                                ob_text = str(ob_val)
                            ob_elem.text = ob_text
                            if self.verbose:
                                print(f"      DEBUG: Wrote OB {ob_text} for {weapon_name}")
                        except Exception as e:
                            if self.verbose:
                                print(f"      ERROR writing OB for {weapon_name}: {e}")
                    


                                        # If this weapon references a module item but has no attacktable in NPC data,
                    # copy the item's attack table onto the NPC weapon entry (FG expects this materialized).
                    if weapon_name and 'attacktable' not in weapon_data:
                        if self.verbose:
                            print(f"      DEBUG: Attempting attacktable copy for {weapon_name} (no attacktable in NPC data)")
                        try:
                            added = self._add_attacktable_from_item(weapon_elem, weapon_name)
                            if self.verbose and added:
                                print(f"      DEBUG: Copied attack table from item for {weapon_name}")
                        except Exception as e:
                            if self.verbose:
                                print(f"      ERROR copying attack table for {weapon_name}: {e}")

                    # Add attack table if present in weapon data (e.g., natural weapons/spells)
                    elif 'attacktable' in weapon_data:
                        attacktable_data = weapon_data['attacktable']
                        if isinstance(attacktable_data, dict):
                            attacktable_elem = ET.SubElement(weapon_elem, 'attacktable')

                            # Add table name
                            if 'name' in attacktable_data:
                                name_elem = ET.SubElement(attacktable_elem, 'name')
                                name_elem.set('type', 'string')
                                if isinstance(attacktable_data['name'], dict):
                                    name_elem.text = attacktable_data['name'].get('_text', '')
                                else:
                                    name_elem.text = str(attacktable_data['name'])

                            # Add table ID
                            if 'tableid' in attacktable_data:
                                tableid_elem = ET.SubElement(attacktable_elem, 'tableid')
                                tableid_elem.set('type', 'string')
                                if isinstance(attacktable_data['tableid'], dict):
                                    tableid_elem.text = attacktable_data['tableid'].get('_text', '')
                                else:
                                    tableid_elem.text = str(attacktable_data['tableid'])

                            if self.verbose:
                                print(f"      DEBUG: Added attack table for {weapon_name}")

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
    
    def add_tokens(self, npc_elem: ET.Element, npc_name: str, yaml_npc: Dict = None):
        """
        Add token elements to NPC
        
        Priority order:
        1. Tokens specified in YAML (can reference other modules)
        2. Token files in tokens/ folder (auto-detected by name)
        3. None (FG generates letter badges)
        
        Args:
            npc_elem: NPC XML element to add tokens to
            npc_name: Display name of the NPC
            yaml_npc: Optional YAML NPC specification
        """
        tokens_added = False
        
        # Priority 1: Check if tokens are specified in YAML
        if yaml_npc and 'tokens' in yaml_npc:
            yaml_tokens = yaml_npc['tokens']
            
            # Add picture token if specified
            if 'picture' in yaml_tokens:
                picture = ET.SubElement(npc_elem, 'picture')
                picture.set('type', 'token')
                picture.text = yaml_tokens['picture']
                tokens_added = True
            
            # Add standard token if specified
            if 'token' in yaml_tokens:
                token = ET.SubElement(npc_elem, 'token')
                token.set('type', 'token')
                token.text = yaml_tokens['token']
                tokens_added = True
            
            # Add 3D flat token if specified
            if 'token3dflat' in yaml_tokens:
                token3d = ET.SubElement(npc_elem, 'token3Dflat')
                token3d.set('type', 'token')
                token3d.text = yaml_tokens['token3dflat']
                tokens_added = True
            
            # If YAML tokens were specified, we're done
            if tokens_added:
                return
        
        # Priority 2: Check for file-based tokens
        # Normalize the NPC name to match token filenames
        normalized_name = self.loader.normalize_npc_name(npc_name)
        
        # Check if we have tokens for this NPC
        if normalized_name not in self.loader.tokens:
            return
        
        tokens = self.loader.tokens[normalized_name]
        
        # Add picture token if available
        if 'picture' in tokens:
            picture = ET.SubElement(npc_elem, 'picture')
            picture.set('type', 'token')
            picture.text = tokens['picture']
        
        # Add standard token if available
        if 'token' in tokens:
            token = ET.SubElement(npc_elem, 'token')
            token.set('type', 'token')
            token.text = tokens['token']
        
        # Add 3D flat token if available
        if 'token3dflat' in tokens:
            token3d = ET.SubElement(npc_elem, 'token3Dflat')
            token3d.set('type', 'token')
            token3d.text = tokens['token3dflat']
    
    def apply_default_weapons(self, npc_data: Dict, npc_name: str) -> Dict:
        """
        Replace melee/missile placeholders with default weapons based on NPC type
        
        Args:
            npc_data: NPC data dictionary
            npc_name: Display name of the NPC (e.g., "Fighter Level 03", "Orc, Lesser")
            
        Returns:
            Modified npc_data with weapons replaced
        """
        if 'weapons' not in npc_data or not npc_data['weapons']:
            return npc_data
        
        # Determine NPC base type
        # 1. Check if this is a custom NPC based on another (check _based_on metadata)
        # 2. Strip level if present (e.g., "Fighter Level 03" -> "Fighter")
        # 3. Use the name as-is
        base_type = npc_data.get('_based_on', npc_name)  # Check metadata first
        
        if self.verbose:
            print(f"    DEBUG: Checking weapons for '{npc_name}', base_type='{base_type}', has _based_on: {'_based_on' in npc_data}")
        
        if ' Level ' in base_type:
            base_type = base_type.split(' Level ')[0]
        
        # Check if we have default weapons for this type
        if base_type not in self.default_weapons:
            if self.verbose:
                print(f"    DEBUG: No default weapons found for '{base_type}'")
            return npc_data
        
        default_config = self.default_weapons[base_type]
        if 'weapons' not in default_config:
            return npc_data
        
        # Find melee and missile placeholders
        weapons = npc_data['weapons']
        melee_key = None
        missile_key = None
        
        for weapon_id, weapon_data in weapons.items():
            if weapon_id.startswith('_'):
                continue
            if isinstance(weapon_data, dict):
                weapon_name = weapon_data.get('name', {}).get('_text', weapon_data.get('name', '')).lower()
                if weapon_name in ['melee', 'weapon']:  # "Weapon" is also a melee placeholder
                    melee_key = weapon_id
                elif weapon_name == 'missile':
                    missile_key = weapon_id
        
        # Apply default weapons
        weapons_to_assign = {}  # slot -> weapon config
        for default_weapon in default_config['weapons']:
            slot = default_weapon.get('slot', 'melee')
            weapons_to_assign[slot] = default_weapon
        
        # Replace or remove weapons based on defaults
        for default_weapon in default_config['weapons']:
            weapon_name = default_weapon['name']
            slot = default_weapon.get('slot', 'melee')
            ob_modifier = default_weapon.get('ob_modifier', 0)
            
            target_key = None
            if slot == 'melee' and melee_key:
                target_key = melee_key
            elif slot == 'missile' and missile_key:
                target_key = missile_key
            elif slot == 'shield':
                # Shields go in a new slot
                target_key = f"id-{len(weapons) + 1:05d}"
            
            if target_key:
                # Get base OB from placeholder if it exists
                base_ob = 0
                if target_key in weapons and 'ob' in weapons[target_key]:
                    ob_data = weapons[target_key]['ob']
                    if isinstance(ob_data, dict):
                        base_ob = int(ob_data.get('_text', 0))
                    else:
                        base_ob = int(ob_data)
                
                # Create weapon entry
                weapons[target_key] = {
                    'name': {'@type': 'string', '_text': weapon_name},
                    'ob': {'@type': 'number', '_text': str(base_ob + ob_modifier)}
                }
                
                if self.verbose:
                    mod_str = f" ({ob_modifier:+d})" if ob_modifier != 0 else ""
                    print(f"    Assigned {weapon_name} to {npc_name} (OB {base_ob + ob_modifier}{mod_str})")
        
        # Remove missile weapon if no missile weapon in defaults (e.g., spell users with staff only)
        if missile_key and 'missile' not in weapons_to_assign:
            if self.verbose:
                print(f"    Removed missile weapon from {npc_name} (not in default weapons)")
            del weapons[missile_key]
        
        return npc_data
    
    def create_npc_from_library(self, npc_data: Dict, use_item_refs: bool = True, yaml_npc: Dict = None) -> ET.Element:
        """
        Create NPC element from complete library data
        
        Note: The caller must assign the element's tag (ID) after creation
        
        Args:
            npc_data: Complete NPC dictionary from library
            use_item_refs: If True, use item references where possible
            yaml_npc: Optional YAML NPC specification (for tokens, etc.)
            
        Returns:
            XML Element with complete stat block (tag will be temporary)
        """
        # Apply default weapons if configured
        npc_name = npc_data.get('_display_name', '')
        if npc_name and self.default_weapons:
            npc_data = self.apply_default_weapons(npc_data, npc_name)
            
            # DEBUG: Check if modifications persist
            if self.verbose and 'weapons' in npc_data:
                print(f"    DEBUG: After apply_default_weapons, weapons are:")
                for w_id, w_data in list(npc_data['weapons'].items())[:3]:
                    if isinstance(w_data, dict):
                        w_name = w_data.get('name', {})
                        if isinstance(w_name, dict):
                            w_name = w_name.get('_text', 'unknown')
                        print(f"      {w_id}: {w_name}")
        
        # Override with YAML weapons if provided
        if yaml_npc and 'weapons' in yaml_npc:
            # Convert YAML weapons list to library format dict
            # This overrides default/base weapons with custom YAML weapons
            npc_data['weapons'] = {}
            for idx, weapon_spec in enumerate(yaml_npc['weapons'], 1):
                weapon_name = weapon_spec.get('weapon')
                ob = weapon_spec.get('ob', 0)
                bonus = weapon_spec.get('bonus', 0)
                
                # Find weapon in item library
                weapon_result = self.library.find_item(weapon_name)
                if weapon_result['found']:
                    weapon_data = weapon_result['entry'].copy()
                    # Set custom OB if specified
                    if ob:
                        weapon_data['ob'] = {'@type': 'number', '_text': str(ob)}
                    if bonus:
                        weapon_data['bonus'] = {'@type': 'number', '_text': str(bonus)}
                    npc_data['weapons'][f'id-{idx:04d}'] = weapon_data
        
        # Override with YAML defences if provided
        if yaml_npc and 'defences' in yaml_npc:
            # Convert YAML defences list to library format dict
            npc_data['defences'] = {}
            for idx, defence_spec in enumerate(yaml_npc['defences'], 1):
                defence_name = defence_spec.get('name')
                melee_bonus = defence_spec.get('melee_bonus', 0)
                missile_bonus = defence_spec.get('missile_bonus', 0)
                
                # Create defence entry
                npc_data['defences'][f'id-{idx:04d}'] = {
                    'name': {'@type': 'string', '_text': defence_name},
                    'melee': {'@type': 'number', '_text': str(melee_bonus)},
                    'missile': {'@type': 'number', '_text': str(missile_bonus)}
                }
        
        # Create element with temporary tag (caller will set the real ID)
        npc_elem = ET.Element('temp')
        
        # Remove token fields from npc_data so FG generates letter badges automatically
        # Empty token fields from library data prevent FG's auto-generation
        for token_field in ['token', 'picture', 'token3Dflat']:
            if token_field in npc_data:
                del npc_data[token_field]
        
        # Ensure nonid_name is set (this is what shows in combat tracker even when not identified)
        if 'nonid_name' not in npc_data:
            npc_data['nonid_name'] = {'@type': 'string', '_text': npc_name}
        
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
            npc_elem = self.create_npc_from_library(result['entry'], use_item_refs=True, yaml_npc=yaml_npc)
            # Update the element's tag to the assigned ID
            npc_elem.tag = npc_id
            self.ensure_auto_letter_token(npc_elem, npc_id, npc_name)
            return npc_elem
        
        # Case 3: Custom NPC based on template
        else:
            based_on = yaml_npc['based_on']
            level = yaml_npc.get('level')
            
            # Collect modifications - both from explicit modifications dict
            # and from top-level attributes (but skip structural fields and weapons/defences)
            modifications = yaml_npc.get('modifications', {}).copy()
            
            # Add top-level attributes as modifications (skip meta and structural fields)
            skip_fields = {'name', 'based_on', 'modifications', 'tokens', 
                          'weapons', 'defences', 'group'}  # weapons/defences handled separately
            # Note: 'level' is NOT skipped - if specified, it overrides the template level
            for key, value in yaml_npc.items():
                if key not in skip_fields and key not in modifications:
                    modifications[key] = value
            
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
            npc_elem = self.create_npc_from_library(result['entry'], use_item_refs=True, yaml_npc=yaml_npc)
            # Update the element's tag to the assigned ID
            npc_elem.tag = npc_id
            self.ensure_auto_letter_token(npc_elem, npc_id, npc_name)
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
                    # Append to tree (this sets the real ID tag)
                    npc_root.append(npc_elem)
                    custom_count += 1
                    # Track this NPC by name (tag is now set by append)
                    npc_name = yaml_npc.get('name')
                    if npc_name:
                        generated_npcs[npc_name] = True  # Just mark as generated
        
        # Step 2: Collect unique NPCs from encounters
        encounter_npcs = {}  # name -> {level, based_on, display_name} mapping
        if self.loader.encounters:
            for encounter in self.loader.encounters:
                for npc_ref in encounter.get('npcs', []):
                    npc_name = npc_ref.get('creature') or npc_ref.get('name')
                    display_name = npc_ref.get('display_name')
                    
                    # If display_name is provided, use it as the actual NPC name
                    # and set based_on to the original npc_name
                    if display_name:
                        final_name = display_name
                        final_based_on = npc_ref.get('based_on') or npc_name
                    else:
                        final_name = npc_name
                        final_based_on = npc_ref.get('based_on')
                    
                    if final_name and final_name not in generated_npcs:
                        # Store unique NPC with its details
                        key = final_name
                        if npc_ref.get('level'):
                            key = f"{final_name}_L{npc_ref['level']}"
                        
                        if key not in encounter_npcs:
                            encounter_npcs[key] = {
                                'name': final_name,
                                'level': npc_ref.get('level'),
                                'based_on': final_based_on
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
                    # Track this NPC by name for battle references
                    generated_npcs[npc_name] = True  # Just mark as generated
        
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
