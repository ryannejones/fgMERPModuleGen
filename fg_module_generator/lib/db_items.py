"""
Items and Parcels XML Generator
Generate <item> and <treasureparcels> sections with proper FG structure
"""

import xml.etree.ElementTree as ET
import re

class ItemGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.item_next_id = 1
        self.parcel_next_id = 1
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
    
    def create_item(self, item):
        """Create an item element with basic structure"""
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
            
            # Base weapon (for weapons with bonuses)
            if 'base_weapon' in props:
                baseweapon = ET.SubElement(item_elem, 'baseweapon')
                baseweapon.set('type', 'string')
                baseweapon.text = props['base_weapon']
                
                # Look up attack table from base weapon
                weapon_data = self.library.get_weapon(props['base_weapon'])
                if weapon_data:
                    attacktable = ET.SubElement(item_elem, 'attacktable')
                    tablename = ET.SubElement(attacktable, 'name')
                    tablename.set('type', 'string')
                    tablename.text = props['base_weapon']
                    tableid = ET.SubElement(attacktable, 'tableid')
                    tableid.set('type', 'string')
                    tableid.text = weapon_data.get('table', 'ALT-01')
            
            # Armor properties
            if 'armor_bonus' in props:
                armorbonus = ET.SubElement(item_elem, 'armorbonus')
                armorbonus.set('type', 'number')
                armorbonus.text = str(props['armor_bonus'])
            
            if 'at' in props:
                at = ET.SubElement(item_elem, 'armortype')
                at.set('type', 'number')
                at.text = str(props['at'])
        
        return item_elem
    
    def parse_item_quantity(self, text):
        """Parse quantity from text like '10 orcish scimitars' or '6 horses'"""
        import re
        
        # Try to match number at start
        match = re.match(r'^(\d+)\s+(.+)$', text.strip())
        if match:
            count = int(match.group(1))
            name = match.group(2)
            return count, name
        
        # No quantity found, default to 1
        return 1, text
    
    def parse_coin_amount(self, text):
        """Parse coin amounts from text like '50gp' or '15 gold pieces'"""
        coins = {}
        
        # Common patterns
        patterns = [
            (r'(\d+)\s*(?:mp|mithril)', 'MP'),
            (r'(\d+)\s*(?:gp|gold)', 'GP'),
            (r'(\d+)\s*(?:sp|silver)', 'SP'),
            (r'(\d+)\s*(?:bp|bronze)', 'BP'),
            (r'(\d+)\s*(?:cp|copper)', 'CP'),
            (r'(\d+)\s*(?:tp|tin)', 'TP'),
            (r'(\d+)\s*(?:ip|iron)', 'IP'),
        ]
        
        text_lower = text.lower()
        for pattern, coin_type in patterns:
            match = re.search(pattern, text_lower)
            if match:
                coins[coin_type] = int(match.group(1))
        
        return coins
    
    def create_coinlist(self):
        """Create standard coinlist structure"""
        coinlist = ET.Element('coinlist')
        
        for i, coin_type in enumerate(self.coin_types, 1):
            coin_id = f"id-{i:05d}"
            coin = ET.SubElement(coinlist, coin_id)
            
            amount = ET.SubElement(coin, 'amount')
            amount.set('type', 'number')
            amount.text = '0'
            
            description = ET.SubElement(coin, 'description')
            description.set('type', 'string')
            description.text = coin_type
        
        return coinlist
    
    def create_parcel(self, parcel):
        """Create a treasure parcel element with proper FG structure"""
        parcel_id = self.get_next_parcel_id()
        parcel_elem = ET.Element(parcel_id)
        
        # Store ID for cross-referencing
        parcel['_id'] = parcel_id
        self.loader.name_to_id['parcel'][parcel['name']] = parcel_id
        
        # Coinlist (required)
        coinlist = self.create_coinlist()
        
        # Parse coins from description and contents
        all_text = parcel.get('description', '') + '\n'
        for content in parcel.get('contents', []):
            if isinstance(content, str):
                all_text += content + '\n'
        
        coins = self.parse_coin_amount(all_text)
        
        # Update coinlist with found coins
        for coin_elem in coinlist:
            desc = coin_elem.find('description')
            if desc is not None and desc.text in coins:
                amount = coin_elem.find('amount')
                if amount is not None:
                    amount.text = str(coins[desc.text])
        
        parcel_elem.append(coinlist)
        
        # Encumbrance (required)
        encumbrance = ET.SubElement(parcel_elem, 'encumbrance')
        load = ET.SubElement(encumbrance, 'load')
        load.set('type', 'number')
        load.text = '0'
        
        # Itemlist (required)
        itemlist = ET.SubElement(parcel_elem, 'itemlist')
        
        # Add items from contents
        item_counter = 1
        for content in parcel.get('contents', []):
            if isinstance(content, dict) and 'item' in content:
                # Reference to custom item - create link
                item_name = content['item']
                item_id_ref = self.loader.name_to_id['item'].get(item_name)
                
                if item_id_ref:
                    item_entry_id = f"id-{item_counter:05d}"
                    item_counter += 1
                    
                    item_entry = ET.SubElement(itemlist, item_entry_id)
                    
                    # Link to the item
                    item_link = ET.SubElement(item_entry, 'link')
                    item_link.set('type', 'windowreference')
                    
                    link_class = ET.SubElement(item_link, 'class')
                    link_class.text = 'item'
                    
                    recordname = ET.SubElement(item_link, 'recordname')
                    recordname.text = f'item.{item_id_ref}'
                    
                    # Name
                    name = ET.SubElement(item_entry, 'name')
                    name.set('type', 'string')
                    name.text = item_name
            
            elif isinstance(content, str):
                # Plain text item - parse quantity and check references
                # Skip if it's just coins (already in coinlist)
                if not self.parse_coin_amount(content):
                    item_entry_id = f"id-{item_counter:05d}"
                    item_counter += 1
                    
                    item_entry = ET.SubElement(itemlist, item_entry_id)
                    
                    # Parse quantity and name
                    item_count, item_name = self.parse_item_quantity(content)
                    
                    # Check if this exact item name is a custom item in our items.yaml
                    # If so, DON'T fuzzy match - we want the custom version with special properties
                    custom_item_id = self.loader.name_to_id['item'].get(item_name)
                    
                    if custom_item_id:
                        # This is a reference to our custom item - create link
                        item_link = ET.SubElement(item_entry, 'link')
                        item_link.set('type', 'windowreference')
                        
                        link_class = ET.SubElement(item_link, 'class')
                        link_class.text = 'item'
                        
                        recordname = ET.SubElement(item_link, 'recordname')
                        recordname.text = f'item.{custom_item_id}'
                        
                        # Name
                        name = ET.SubElement(item_entry, 'name')
                        name.set('type', 'string')
                        name.text = item_name
                        
                        # Count
                        count = ET.SubElement(item_entry, 'count')
                        count.set('type', 'number')
                        count.text = str(item_count)
                    else:
                        # Not a custom item - try to find in reference library
                        matched_name = self.library.find_item_fuzzy(item_name)
                        item_ref = self.library.get_item_reference(matched_name) if matched_name else None
                        # Not a custom item - try to find in reference library
                        matched_name = self.library.find_item_fuzzy(item_name)
                        item_ref = self.library.get_item_reference(matched_name) if matched_name else None
                        
                        if item_ref:
                            # Create link to reference item
                            item_link = ET.SubElement(item_entry, 'link')
                            item_link.set('type', 'windowreference')
                            
                            link_class = ET.SubElement(item_link, 'class')
                            link_class.text = 'item'
                            
                            recordname = ET.SubElement(item_link, 'recordname')
                            recordname.text = item_ref
                            
                            # Name
                            name = ET.SubElement(item_entry, 'name')
                            name.set('type', 'string')
                            name.text = item_name
                            
                            # Count
                            count = ET.SubElement(item_entry, 'count')
                            count.set('type', 'number')
                            count.text = str(item_count)
                        else:
                            # Create simple local item
                            # Name
                            name = ET.SubElement(item_entry, 'name')
                            name.set('type', 'string')
                            name.text = item_name
                            
                            # Count
                            count = ET.SubElement(item_entry, 'count')
                            count.set('type', 'number')
                            count.text = str(item_count)
                            
                            # Type
                            itemtype = ET.SubElement(item_entry, 'type')
                            itemtype.set('type', 'string')
                            itemtype.text = 'Item'
        
        # Name
        name = ET.SubElement(parcel_elem, 'name')
        name.set('type', 'string')
        name.text = parcel['name']
        
        # Temp field (sometimes present in FG parcels)
        temp = ET.SubElement(parcel_elem, 'temp')
        temp.set('type', 'string')
        temp.text = parcel.get('description', '')
        
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
        
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t", encoding='utf-8').decode('utf-8')
