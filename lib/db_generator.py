"""
DB.xml Generator - Assemble complete db.xml from all sections
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

class DBGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
    
    def create_library_section(self):
        """Create the library section with module info"""
        library = ET.Element('library')
        
        # Module entry
        module_name = self.loader.config['name']
        module_entry = ET.SubElement(library, module_name)
        module_entry.set('static', 'true')
        
        # Name
        name = ET.SubElement(module_entry, 'name')
        name.set('type', 'string')
        name.text = self.loader.config['display_name']
        
        # Category
        categoryname = ET.SubElement(module_entry, 'categoryname')
        categoryname.set('type', 'string')
        categoryname.text = self.loader.config.get('category', 'Custom Modules')
        
        # Entry list - what content types are included
        entries = ET.SubElement(module_entry, 'entries')
        
        # Add entries for each content type that exists
        if self.loader.encounters:
            battle_entry = ET.SubElement(entries, 'battle')
            battle_link = ET.SubElement(battle_entry, 'librarylink')
            battle_link.set('type', 'windowreference')
            
            battle_class = ET.SubElement(battle_link, 'class')
            battle_class.text = 'reference_list'
            
            battle_recordname = ET.SubElement(battle_link, 'recordname')
            battle_recordname.text = '..'
            
            battle_name = ET.SubElement(battle_entry, 'name')
            battle_name.set('type', 'string')
            battle_name.text = 'Encounters'
            
            battle_recordtype = ET.SubElement(battle_entry, 'recordtype')
            battle_recordtype.set('type', 'string')
            battle_recordtype.text = 'battle'
        
        if self.loader.stories:
            story_entry = ET.SubElement(entries, 'story')
            story_link = ET.SubElement(story_entry, 'librarylink')
            story_link.set('type', 'windowreference')
            
            story_class = ET.SubElement(story_link, 'class')
            story_class.text = 'reference_list'
            
            story_recordname = ET.SubElement(story_link, 'recordname')
            story_recordname.text = '..'
            
            story_name = ET.SubElement(story_entry, 'name')
            story_name.set('type', 'string')
            story_name.text = 'Stories'
            
            story_recordtype = ET.SubElement(story_entry, 'recordtype')
            story_recordtype.set('type', 'string')
            story_recordtype.text = 'story'
        
        if self.loader.npcs:
            npc_entry = ET.SubElement(entries, 'npc')
            npc_link = ET.SubElement(npc_entry, 'librarylink')
            npc_link.set('type', 'windowreference')
            
            npc_class = ET.SubElement(npc_link, 'class')
            npc_class.text = 'reference_list'
            
            npc_recordname = ET.SubElement(npc_link, 'recordname')
            npc_recordname.text = '..'
            
            npc_name = ET.SubElement(npc_entry, 'name')
            npc_name.set('type', 'string')
            npc_name.text = 'NPCs'
            
            npc_recordtype = ET.SubElement(npc_entry, 'recordtype')
            npc_recordtype.set('type', 'string')
            npc_recordtype.text = 'npc'
        
        if self.loader.items:
            item_entry = ET.SubElement(entries, 'item')
            item_link = ET.SubElement(item_entry, 'librarylink')
            item_link.set('type', 'windowreference')
            
            item_class = ET.SubElement(item_link, 'class')
            item_class.text = 'reference_list'
            
            item_recordname = ET.SubElement(item_link, 'recordname')
            item_recordname.text = '..'
            
            item_name = ET.SubElement(item_entry, 'name')
            item_name.set('type', 'string')
            item_name.text = 'Items'
            
            item_recordtype = ET.SubElement(item_entry, 'recordtype')
            item_recordtype.set('type', 'string')
            item_recordtype.text = 'item'
        
        if self.loader.parcels:
            parcel_entry = ET.SubElement(entries, 'treasureparcel')
            parcel_link = ET.SubElement(parcel_entry, 'librarylink')
            parcel_link.set('type', 'windowreference')
            
            parcel_class = ET.SubElement(parcel_link, 'class')
            parcel_class.text = 'reference_list'
            
            parcel_recordname = ET.SubElement(parcel_link, 'recordname')
            parcel_recordname.text = '..'
            
            parcel_name = ET.SubElement(parcel_entry, 'name')
            parcel_name.set('type', 'string')
            parcel_name.text = 'Treasure Parcels'
            
            parcel_recordtype = ET.SubElement(parcel_entry, 'recordtype')
            parcel_recordtype.set('type', 'string')
            parcel_recordtype.text = 'treasureparcel'
        
        if self.loader.images:
            image_entry = ET.SubElement(entries, 'image')
            image_link = ET.SubElement(image_entry, 'librarylink')
            image_link.set('type', 'windowreference')
            
            image_class = ET.SubElement(image_link, 'class')
            image_class.text = 'reference_list'
            
            image_recordname = ET.SubElement(image_link, 'recordname')
            image_recordname.text = '..'
            
            image_name = ET.SubElement(image_entry, 'name')
            image_name.set('type', 'string')
            image_name.text = 'Images'
            
            image_recordtype = ET.SubElement(image_entry, 'recordtype')
            image_recordtype.set('type', 'string')
            image_recordtype.text = 'image'
        
        return library
    
    def merge_xml_sections(self, *xml_roots):
        """Merge multiple XML sections into root element"""
        root = ET.Element('root')
        root.set('version', '4')
        
        # Add each section
        for xml_section in xml_roots:
            if xml_section is not None:
                root.append(xml_section)
        
        return root
    
    def generate(self, battle_xml=None, story_xml=None, npc_xml=None, 
                 item_xml=None, parcel_xml=None, image_xml=None):
        """Generate complete db.xml"""
        
        if self.verbose:
            print("  Assembling db.xml...")
        
        # Create root element
        root = ET.Element('root')
        root.set('version', '5')
        root.set('dataversion', '20250919')
        root.set('release', '2.3|CoreRPG:7')
        
        # Add library section (must be first)
        library = self.create_library_section()
        root.append(library)
        
        # Add content sections in proper order
        if battle_xml is not None:
            root.append(battle_xml)
        
        if item_xml is not None:
            root.append(item_xml)
        
        if npc_xml is not None:
            root.append(npc_xml)
        
        if story_xml is not None:
            root.append(story_xml)
        
        if parcel_xml is not None:
            root.append(parcel_xml)
        
        if image_xml is not None:
            root.append(image_xml)
        
        if self.verbose:
            sections = []
            if battle_xml is not None: sections.append('battles')
            if story_xml is not None: sections.append('stories')
            if npc_xml is not None: sections.append('npcs')
            if item_xml is not None: sections.append('items')
            if parcel_xml is not None: sections.append('parcels')
            if image_xml is not None: sections.append('images')
            
            print(f"  [OK] Assembled {len(sections)} sections: {', '.join(sections)}")
        
        return root
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t", encoding='utf-8').decode('utf-8')
    
    def write_to_file(self, root, filepath):
        """Write XML to file"""
        xml_string = self.to_xml_string(root)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        if self.verbose:
            print(f"  [OK] Wrote db.xml to {filepath}")
