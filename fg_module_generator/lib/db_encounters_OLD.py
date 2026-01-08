"""
Encounter XML Generator - Generate <encounter> section (stories) from stories.yaml
Note: In Fantasy Grounds, the "Stories" tab uses <encounter> XML tags
"""

import xml.etree.ElementTree as ET

class EncounterGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.next_id = 1
    
    def get_next_id(self):
        """Get next encounter ID"""
        enc_id = f"id-{self.next_id:05d}"
        self.next_id += 1
        return enc_id
    
    def format_text_content(self, text):
        """Format text content, converting \n to actual line breaks"""
        if not text:
            return ""
        # Replace literal \n with actual newlines
        return text.replace('\\n', '\n')
    
    def create_text_element(self, section):
        """Create a formatted text element from a story section"""
        section_type = section.get('type')
        text = section.get('text', '')
        
        if section_type == 'header':
            elem = ET.Element('h')
            elem.text = self.format_text_content(text)
            return elem
        
        elif section_type == 'read_aloud':
            elem = ET.Element('frame')
            elem.text = self.format_text_content(text)
            return elem
        
        elif section_type == 'gm_notes':
            elem = ET.Element('p')
            elem.text = self.format_text_content(text)
            return elem
        
        elif section_type.startswith('link_'):
            # Create a link list
            linklist = ET.Element('linklist')
            link = ET.SubElement(linklist, 'link')
            
            # Determine link target
            if section_type == 'link_encounter':
                link.set('class', 'battle')
                enc_name = section.get('encounter_name')
                enc_id = self.loader.name_to_id['encounter'].get(enc_name)
                if enc_id:
                    link.set('recordname', f'battle.{enc_id}')
                link_text = section.get('link_text', f'Encounter: {enc_name}')
            
            elif section_type == 'link_npc':
                link.set('class', 'npc')
                npc_name = section.get('npc_name')
                # For library NPCs
                if self.library.creature_exists(npc_name):
                    recordname = f'reference.npcs.{npc_name.lower().replace(" ", "")}@Character Law'
                else:
                    # Custom NPC
                    npc_id = self.loader.name_to_id['npc'].get(npc_name)
                    recordname = f'npc.{npc_id}' if npc_id else f'npc.{npc_name.lower().replace(" ", "_")}'
                link.set('recordname', recordname)
                link_text = section.get('link_text', f'NPC: {npc_name}')
            
            elif section_type == 'link_item':
                link.set('class', 'item')
                item_name = section.get('item_name')
                item_id = self.loader.name_to_id['item'].get(item_name)
                if item_id:
                    link.set('recordname', f'item.{item_id}')
                link_text = section.get('link_text', f'Item: {item_name}')
            
            elif section_type == 'link_parcel':
                link.set('class', 'treasureparcel')
                parcel_name = section.get('parcel_name')
                parcel_id = self.loader.name_to_id['parcel'].get(parcel_name)
                if parcel_id:
                    link.set('recordname', f'treasureparcel.{parcel_id}')
                link_text = section.get('link_text', f'Treasure: {parcel_name}')
            
            elif section_type == 'link_image':
                link.set('class', 'image')
                image_name = section.get('image_name')
                image_id = self.loader.name_to_id['image'].get(image_name)
                if image_id:
                    link.set('recordname', f'image.{image_id}')
                link_text = section.get('link_text', f'Map: {image_name}')
            
            else:
                link_text = 'Unknown Link'
            
            link.text = link_text
            return linklist
        
        # Unknown section type - return empty paragraph
        elem = ET.Element('p')
        elem.text = f'[Unknown section type: {section_type}]'
        return elem
    
    def create_encounter(self, story):
        """Create an encounter (story) element"""
        enc_id = self.get_next_id()
        encounter = ET.Element(enc_id)
        
        # Store ID for cross-referencing
        story['_id'] = enc_id
        self.loader.name_to_id['story'][story['name']] = enc_id
        
        # Name
        name = ET.SubElement(encounter, 'name')
        name.set('type', 'string')
        name.text = story['name']
        
        # Text content (formattedtext)
        text_root = ET.SubElement(encounter, 'text')
        text_root.set('type', 'formattedtext')
        
        # Add all sections
        for section in story.get('sections', []):
            text_elem = self.create_text_element(section)
            if text_elem is not None:
                text_root.append(text_elem)
        
        return encounter
    
    def generate(self):
        """Generate the complete <encounter> section"""
        if not self.loader.stories:
            return None
        
        if self.verbose:
            print(f"  Generating {len(self.loader.stories)} story entries...")
        
        # Create root encounter element
        encounter_root = ET.Element('encounter')
        
        for story in self.loader.stories:
            encounter = self.create_encounter(story)
            encounter_root.append(encounter)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.stories)} story entries")
        
        return encounter_root
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
