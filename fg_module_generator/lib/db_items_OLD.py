"""
Items and Parcels XML Generator
Generate <item> and <treasureparcel> sections
"""

import xml.etree.ElementTree as ET

class ItemGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.item_next_id = 1
        self.parcel_next_id = 1
    
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
    
    def create_item(self, item):
        """Create an item element"""
        item_id = self.get_next_item_id()
        item_elem = ET.Element(item_id)
        
        # Store ID for cross-referencing
        item['_id'] = item_id
        self.loader.name_to_id['item'][item['name']] = item_id
        
        # Name
        name = ET.SubElement(item_elem, 'name')
        name.set('type', 'string')
        name.text = item['name']
        
        # Type
        itemtype = ET.SubElement(item_elem, 'type')
        itemtype.set('type', 'string')
        itemtype.text = item.get('type', 'Item')
        
        # Count
        count = ET.SubElement(item_elem, 'count')
        count.set('type', 'number')
        count.text = str(item.get('count', 1))
        
        # Description
        if 'description' in item:
            description = ET.SubElement(item_elem, 'description')
            description.set('type', 'formattedtext')
            p = ET.SubElement(description, 'p')
            p.text = item['description']
        
        # Properties
        if 'properties' in item:
            props = item['properties']
            
            # Weapon bonus
            if 'weapon_bonus' in props:
                bonus = ET.SubElement(item_elem, 'bonus')
                bonus.set('type', 'number')
                bonus.text = str(props['weapon_bonus'])
            
            # Base weapon
            if 'base_weapon' in props:
                baseweapon = ET.SubElement(item_elem, 'baseweapon')
                baseweapon.set('type', 'string')
                baseweapon.text = props['base_weapon']
            
            # Armor bonus
            if 'armor_bonus' in props:
                armorbonus = ET.SubElement(item_elem, 'armorbonus')
                armorbonus.set('type', 'number')
                armorbonus.text = str(props['armor_bonus'])
            
            # Armor Type
            if 'at' in props:
                at = ET.SubElement(item_elem, 'armortype')
                at.set('type', 'number')
                at.text = str(props['at'])
            
            # Spell adder
            if 'spell_adder' in props:
                spelladder = ET.SubElement(item_elem, 'spelladder')
                spelladder.set('type', 'number')
                spelladder.text = str(props['spell_adder'])
            
            # Spell lists (which spell lists affected)
            if 'spell_lists' in props:
                spelllists = ET.SubElement(item_elem, 'spelllists')
                spelllists.set('type', 'string')
                spelllists.text = props['spell_lists']
            
            # Power Point multiplier
            if 'pp_multiplier' in props:
                ppmult = ET.SubElement(item_elem, 'ppmultiplier')
                ppmult.set('type', 'number')
                ppmult.text = str(props['pp_multiplier'])
            
            # Skill bonus
            if 'skill_bonus' in props:
                skillbonus = ET.SubElement(item_elem, 'skillbonus')
                skillbonus.set('type', 'number')
                skillbonus.text = str(props['skill_bonus'])
            
            # Which skills
            if 'skills' in props:
                skills = ET.SubElement(item_elem, 'skills')
                skills.set('type', 'string')
                skills.text = props['skills']
            
            # Healing
            if 'healing' in props:
                healing = ET.SubElement(item_elem, 'healing')
                healing.set('type', 'string')
                healing.text = str(props['healing'])
            
            # Healing bonus
            if 'healing_bonus' in props:
                healbonus = ET.SubElement(item_elem, 'healingbonus')
                healbonus.set('type', 'number')
                healbonus.text = str(props['healing_bonus'])
            
            # Special properties (free-form text)
            if 'special' in props:
                special = ET.SubElement(item_elem, 'special')
                special.set('type', 'formattedtext')
                p = ET.SubElement(special, 'p')
                p.text = props['special']
            
            # Curse
            if 'curse' in props:
                curse = ET.SubElement(item_elem, 'curse')
                curse.set('type', 'formattedtext')
                p = ET.SubElement(curse, 'p')
                p.text = props['curse']
            
            # Apparent effect (for cursed items)
            if 'apparent_effect' in props:
                apparent = ET.SubElement(item_elem, 'apparenteffect')
                apparent.set('type', 'string')
                apparent.text = props['apparent_effect']
        
        return item_elem
    
    def create_parcel(self, parcel):
        """Create a treasure parcel element"""
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
        
        # Contents
        if 'contents' in parcel:
            contents = ET.SubElement(parcel_elem, 'contents')
            contents.set('type', 'formattedtext')
            
            for content in parcel['contents']:
                if isinstance(content, dict) and 'item' in content:
                    # Reference to custom item - create link
                    item_name = content['item']
                    item_id = self.loader.name_to_id['item'].get(item_name)
                    
                    if item_id:
                        linklist = ET.SubElement(contents, 'linklist')
                        link = ET.SubElement(linklist, 'link')
                        link.set('class', 'item')
                        link.set('recordname', f'item.{item_id}')
                        link.text = item_name
                    else:
                        # Fallback to text
                        p = ET.SubElement(contents, 'p')
                        p.text = f'• {item_name}'
                else:
                    # Plain text item
                    p = ET.SubElement(contents, 'p')
                    p.text = f'• {content}'
        
        return parcel_elem
    
    def generate_items(self):
        """Generate the <item> section"""
        if not self.loader.items:
            return None
        
        if self.verbose:
            print(f"  Generating {len(self.loader.items)} items...")
        
        item_root = ET.Element('item')
        
        for item in self.loader.items:
            item_elem = self.create_item(item)
            item_root.append(item_elem)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.items)} items")
        
        return item_root
    
    def generate_parcels(self):
        """Generate the <treasureparcels> section"""
        if not self.loader.parcels:
            return None
        
        if self.verbose:
            print(f"  Generating {len(self.loader.parcels)} treasure parcels...")
        
        parcel_root = ET.Element('treasureparcels')
        
        for parcel in self.loader.parcels:
            parcel_elem = self.create_parcel(parcel)
            parcel_root.append(parcel_elem)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.parcels)} treasure parcels")
        
        return parcel_root
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
