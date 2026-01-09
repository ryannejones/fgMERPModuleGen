"""
Items and Parcels XML Generator v0.11
Generates item definitions that NPCs can reference
When items are looted by players, FG automatically copies full data
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any


class ItemGenerator:
    """
    Generates Item XML with complete definitions
    
    Features:
    - Complete item data in module item list
    - NPCs reference these items
    - FG copies data when items added to character inventory
    - Treasure parcels can reference items
    """
    
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.item_next_id = 1
        self.parcel_next_id = 1
        self.parcel_item_entry_id = 1  # Separate counter for parcel item entries
        self.coin_types = ['MP', 'GP', 'SP', 'BP', 'CP', 'TP', 'IP']
    
    def get_next_item_id(self):
        """Get next item ID"""
        item_id = f"id-{self.item_next_id:05d}"
        self.item_next_id += 1
        return item_id
    
    def get_next_parcel_id(self):
        """Get next parcel ID"""
        parcel_id = f"id-{self.parcel_next_id:05d}"
        self.parcel_next_id += 1
        return parcel_id
    
    def dict_to_xml(self, data: Dict[str, Any], parent: ET.Element):
        """
        Recursively convert dictionary to XML
        """
        for key, value in data.items():
            if key.startswith('_'):
                # Skip metadata fields
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
                    self.dict_to_xml(value, elem)
            
            elif isinstance(value, list):
                # Multiple items with same tag
                for item in value:
                    elem = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        self.dict_to_xml(item, elem)
                    else:
                        elem.text = str(item)
            
            else:
                # Simple value
                elem = ET.SubElement(parent, key)
                elem.text = str(value)
    
    def create_item_from_library(self, item_data: Dict) -> ET.Element:
        """
        Create item element from complete library data
        
        Args:
            item_data: Complete item dictionary from library
            
        Returns:
            XML Element with complete stat block
        """
        item_id = self.get_next_item_id()
        item_elem = ET.Element(item_id)
        
        # Convert the complete item data to XML
        self.dict_to_xml(item_data, item_elem)
        
        return item_elem
    
    def create_item_from_yaml(self, yaml_item: Dict) -> ET.Element:
        """
        Create item from YAML specification
        
        This creates COMPLETE item definitions in the module's item list
        NPCs will reference these, players will get copies when looted
        
        Args:
            yaml_item: Item specification from YAML
            
        Returns:
            XML Element or None if not found
        """
        item_name = yaml_item.get('name')
        if not item_name:
            print(f"  WARNING: Item without name: {yaml_item}")
            return None
        
        # Case 1: Find existing item
        if 'based_on' not in yaml_item:
            result = self.library.find_item(item_name)
            
            if not result['found']:
                print(f"  WARNING: Item '{item_name}' not found in library")
                if result.get('suggestions'):
                    print(f"    Suggestions: {', '.join(result['suggestions'][:3])}")
                return None
            
            if self.verbose:
                print(f"  Found '{item_name}' via {result['method']}: {result['matched_name']}")
            
            # Store ID for cross-referencing
            item_id = self.get_next_item_id()
            self.loader.name_to_id['item'][item_name] = item_id
            
            # Create XML from library data
            item_elem = self.create_item_from_library(result['entry'])
            
            # Override count if specified in YAML
            if 'count' in yaml_item:
                count_elem = item_elem.find('count')
                if count_elem is not None:
                    count_elem.text = str(yaml_item['count'])
                else:
                    count = ET.SubElement(item_elem, 'count')
                    count.set('type', 'number')
                    count.text = str(yaml_item['count'])
            
            return item_elem
        
        # Case 2: Custom item based on template
        else:
            based_on = yaml_item['based_on']
            modifications = yaml_item.get('modifications', {})
            
            result = self.library.create_custom_item(
                item_name,
                based_on,
                modifications
            )
            
            if not result['success']:
                print(f"  WARNING: Could not create custom item '{item_name}'")
                print(f"    {result['error']}")
                if result.get('suggestions'):
                    print(f"    Suggestions: {', '.join(result['suggestions'][:3])}")
                return None
            
            if self.verbose:
                print(f"  Created custom '{item_name}' based on {result['based_on']}")
            
            # Store ID for cross-referencing
            item_id = self.get_next_item_id()
            self.loader.name_to_id['item'][item_name] = item_id
            
            # Create XML from custom data
            item_elem = self.create_item_from_library(result['entry'])
            
            # Override count if specified
            if 'count' in yaml_item:
                count_elem = item_elem.find('count')
                if count_elem is not None:
                    count_elem.text = str(yaml_item['count'])
                else:
                    count = ET.SubElement(item_elem, 'count')
                    count.set('type', 'number')
                    count.text = str(yaml_item['count'])
            
            return item_elem
    
    def create_treasure_parcel(self, parcel):
        """
        Create a treasure parcel element
        
        Parcels can reference items from the module item list
        When distributed to characters, FG copies the item data
        """
        parcel_id = self.get_next_parcel_id()
        parcel_elem = ET.Element(parcel_id)
        
        # Store ID for cross-referencing
        parcel['_id'] = parcel_id
        self.loader.name_to_id['parcel'][parcel['name']] = parcel_id
        
        # Name
        name = ET.SubElement(parcel_elem, 'name')
        name.set('type', 'string')
        name.text = parcel['name']
        
        # Description
        if 'description' in parcel:
            description = ET.SubElement(parcel_elem, 'description')
            description.set('type', 'formattedtext')
            p = ET.SubElement(description, 'p')
            p.text = parcel['description']
        
        # Items in parcel - REFERENCE module items
        if 'items' in parcel and parcel['items']:
            items = ET.SubElement(parcel_elem, 'itemlist')
            for item in parcel['items']:
                # Use separate counter for parcel entries (not the main item counter!)
                item_entry_id = f"id-{self.parcel_item_entry_id:05d}"
                self.parcel_item_entry_id += 1
                item_entry = ET.SubElement(items, item_entry_id)
                
                item_name = item.get('name')
                
                # Create reference to module item
                if item_name and item_name in self.loader.name_to_id['item']:
                    link = ET.SubElement(item_entry, 'link')
                    link.set('type', 'windowreference')
                    
                    link_class = ET.SubElement(link, 'class')
                    link_class.text = 'item'
                    
                    link_record = ET.SubElement(link, 'recordname')
                    link_record.text = f"item.{self.loader.name_to_id['item'][item_name]}"
                    
                    # Count
                    count = ET.SubElement(item_entry, 'count')
                    count.set('type', 'number')
                    count.text = str(item.get('count', 1))
                else:
                    # Item not in module list - embed data (fallback)
                    if self.verbose:
                        print(f"    Warning: Item '{item_name}' in parcel but not in module item list")
                    
                    # Create basic item entry
                    name_elem = ET.SubElement(item_entry, 'name')
                    name_elem.set('type', 'string')
                    name_elem.text = item_name
                    
                    count = ET.SubElement(item_entry, 'count')
                    count.set('type', 'number')
                    count.text = str(item.get('count', 1))
        
        # Coins
        if 'coins' in parcel:
            coins = ET.SubElement(parcel_elem, 'coins')
            for coin_type in self.coin_types:
                if coin_type in parcel['coins']:
                    coin_elem = ET.SubElement(coins, coin_type.lower())
                    coin_elem.set('type', 'number')
                    coin_elem.text = str(parcel['coins'][coin_type])
        
        return parcel_elem
    
    def generate_items(self):
        """Generate the complete <item> section with full definitions"""
        if not self.loader.items:
            return None
        
        if self.verbose:
            print(f"\nGenerating Items...")
            print(f"  Processing {len(self.loader.items)} items...")
            print(f"  These will be the master definitions that NPCs reference")
        
        # Create root item element
        item_root = ET.Element('item')
        
        generated_count = 0
        for yaml_item in self.loader.items:
            item_elem = self.create_item_from_yaml(yaml_item)
            if item_elem is not None:
                item_root.append(item_elem)
                generated_count += 1
        
        if self.verbose:
            print(f"  [OK] Generated {generated_count}/{len(self.loader.items)} items")
            print(f"  NPCs can now reference these items")
        
        if generated_count == 0:
            return None
        
        return item_root
    
    def generate_parcels(self):
        """Generate the complete <treasureparcels> section"""
        if not self.loader.parcels:
            return None
        
        if self.verbose:
            print(f"\nGenerating Treasure Parcels...")
            print(f"  Processing {len(self.loader.parcels)} parcels...")
            print(f"  Parcels will reference module items")
        
        # Create root parcel element
        parcel_root = ET.Element('treasureparcels')
        
        for parcel in self.loader.parcels:
            parcel_elem = self.create_treasure_parcel(parcel)
            parcel_root.append(parcel_elem)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.parcels)} treasure parcels")
        
        return parcel_root
    
    def generate(self):
        """Generate both items and parcels"""
        items = self.generate_items()
        parcels = self.generate_parcels()
        return items, parcels
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
