"""
Story XML Generator - Generate <reference><refmanualdata> section (stories) from stories.yaml
Note: Fantasy Grounds uses <reference><refmanualdata> with <blocks> for Stories
"""

import xml.etree.ElementTree as ET

class StoryGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.next_id = 1
        self.block_next_id = 1
    
    def get_next_id(self):
        """Get next story ID"""
        story_id = f"id-{self.next_id:05d}"
        self.next_id += 1
        return story_id
    
    def get_next_block_id(self):
        """Get next block ID"""
        block_id = f"id-{self.block_next_id:05d}"
        self.block_next_id += 1
        return block_id
    
    def format_text_content(self, text):
        """Format text content, converting \n to actual line breaks"""
        if not text:
            return ""
        return text.replace('\\n', '\n')
    
    def create_text_block(self, section):
        """Create a text block from a story section"""
        block_id = self.get_next_block_id()
        block = ET.Element(block_id)
        
        # Alignment
        align = ET.SubElement(block, 'align')
        align.set('type', 'string')
        align.text = 'left'
        
        # Block type
        blocktype = ET.SubElement(block, 'blocktype')
        blocktype.set('type', 'string')
        blocktype.text = 'singletext'
        
        # Frame type based on section type
        frame = ET.SubElement(block, 'frame')
        frame.set('type', 'string')
        
        section_type = section.get('type')
        if section_type == 'header':
            frame.text = 'text4'  # Header frame
        elif section_type == 'read_aloud':
            frame.text = 'text2'  # Read-aloud frame
        else:
            frame.text = 'noframe'  # No frame for GM notes
        
        # Text content
        text_elem = ET.SubElement(block, 'text')
        text_elem.set('type', 'formattedtext')
        
        text_content = self.format_text_content(section.get('text', ''))
        
        if section_type == 'header':
            h = ET.SubElement(text_elem, 'h')
            h.text = text_content
        elif section_type == 'read_aloud':
            frame_elem = ET.SubElement(text_elem, 'frame')
            frame_elem.text = text_content
        else:  # gm_notes or other
            p = ET.SubElement(text_elem, 'p')
            p.text = text_content
        
        return block
    
    def create_link_block(self, section):
        """Create a link block from a story section"""
        block_id = self.get_next_block_id()
        block = ET.Element(block_id)
        
        # Alignment
        align = ET.SubElement(block, 'align')
        align.set('type', 'string')
        align.text = 'left'
        
        # Block type
        blocktype = ET.SubElement(block, 'blocktype')
        blocktype.set('type', 'string')
        blocktype.text = 'singletext'
        
        # Frame
        frame = ET.SubElement(block, 'frame')
        frame.set('type', 'string')
        frame.text = 'noframe'
        
        # Text with link
        text_elem = ET.SubElement(block, 'text')
        text_elem.set('type', 'formattedtext')
        
        linklist = ET.SubElement(text_elem, 'linklist')
        link = ET.SubElement(linklist, 'link')
        
        section_type = section.get('type')
        
        if section_type == 'link_encounter':
            link.set('class', 'battle')
            enc_name = section.get('encounter_name')
            enc_id = self.loader.name_to_id['encounter'].get(enc_name)
            if enc_id:
                link.set('recordname', f'battle.{enc_id}')
            link.text = section.get('link_text', f'Encounter: {enc_name}')
        
        elif section_type == 'link_npc':
            link.set('class', 'npc')
            npc_name = section.get('npc_name')
            result = self.library.find_npc(npc_name)
            if result.get('found') or result.get('suggestions'):
                recordname = f'reference.npcs.{npc_name.lower().replace(" ", "")}@Character Law'
            else:
                npc_id = self.loader.name_to_id['npc'].get(npc_name)
                recordname = f'npc.{npc_id}' if npc_id else f'npc.{npc_name.lower().replace(" ", "_")}'
            link.set('recordname', recordname)
            link.text = section.get('link_text', f'NPC: {npc_name}')
        
        elif section_type == 'link_item':
            link.set('class', 'item')
            item_name = section.get('item_name')
            item_id = self.loader.name_to_id['item'].get(item_name)
            if item_id:
                link.set('recordname', f'item.{item_id}')
            link.text = section.get('link_text', f'Item: {item_name}')
        
        elif section_type == 'link_parcel':
            link.set('class', 'treasureparcel')
            parcel_name = section.get('parcel_name')
            parcel_id = self.loader.name_to_id['parcel'].get(parcel_name)
            if parcel_id:
                link.set('recordname', f'treasureparcel.{parcel_id}')
            link.text = section.get('link_text', f'Treasure: {parcel_name}')
        
        elif section_type == 'link_image':
            link.set('class', 'image')
            image_name = section.get('image_name')
            image_id = self.loader.name_to_id['image'].get(image_name)
            if image_id:
                link.set('recordname', f'image.{image_id}')
            link.text = section.get('link_text', f'Map: {image_name}')
        
        return block
    
    def create_story(self, story):
        """Create a story element (refmanualdata entry)"""
        story_id = self.get_next_id()
        story_elem = ET.Element(story_id)
        
        # Store ID for cross-referencing
        story['_id'] = story_id
        self.loader.name_to_id['story'][story['name']] = story_id
        
        # Blocks container
        blocks = ET.SubElement(story_elem, 'blocks')
        
        # Add all sections as blocks
        for section in story.get('sections', []):
            section_type = section.get('type')
            
            if section_type.startswith('link_'):
                block = self.create_link_block(section)
            else:
                block = self.create_text_block(section)
            
            blocks.append(block)
        
        # Name
        name = ET.SubElement(story_elem, 'name')
        name.set('type', 'string')
        name.text = story['name']
        
        # Empty text element (required by FG)
        text = ET.SubElement(story_elem, 'text')
        text.set('type', 'formattedtext')
        
        return story_elem
    
    def generate(self):
        """Generate the complete <reference> section with <refmanualdata>"""
        if not self.loader.stories:
            return None
        
        if self.verbose:
            print(f"  Generating {len(self.loader.stories)} story entries...")
        
        # Create reference element
        reference = ET.Element('reference')
        
        # Create refmanualdata container
        refmanualdata = ET.SubElement(reference, 'refmanualdata')
        
        # Add all stories
        for story in self.loader.stories:
            story_elem = self.create_story(story)
            refmanualdata.append(story_elem)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.stories)} story entries")
        
        return reference
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t", encoding='utf-8').decode('utf-8')
