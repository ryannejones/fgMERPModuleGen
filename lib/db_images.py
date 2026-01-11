"""
Images XML Generator - Generate <image> section from images.yaml
"""

import xml.etree.ElementTree as ET

class ImageGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.next_id = 1
    
    def get_next_id(self):
        """Get next image ID"""
        image_id = f"id-{self.next_id:05d}"
        self.next_id += 1
        return image_id
    
    def create_image(self, image):
        """Create an image element"""
        image_id = self.get_next_id()
        image_elem = ET.Element(image_id)
        
        # Store ID for cross-referencing
        image['_id'] = image_id
        self.loader.name_to_id['image'][image['name']] = image_id
        
        # Image data
        image_data = ET.SubElement(image_elem, 'image')
        image_data.set('type', 'image')
        
        # Layers
        layers = ET.SubElement(image_data, 'layers')
        
        # Single layer with the image file
        layer = ET.SubElement(layers, 'layer')
        
        # Layer name (filename)
        name_elem = ET.SubElement(layer, 'name')
        filename = image.get('file', 'unknown.jpg')
        name_elem.text = filename
        
        # Layer ID (required by FG)
        id_elem = ET.SubElement(layer, 'id')
        id_elem.text = '0'
        
        # Parent ID (required by FG)
        parentid_elem = ET.SubElement(layer, 'parentid')
        parentid_elem.text = '-6'
        
        # Layer type (required by FG)
        type_elem = ET.SubElement(layer, 'type')
        type_elem.text = 'image'
        
        # Bitmap path (relative to module)
        bitmap = ET.SubElement(layer, 'bitmap')
        bitmap.text = f"images/{filename}"
        
        # Add basic grid settings (5ft squares, standard for D&D/MERP)
        gridsize = ET.SubElement(image_data, 'gridsize')
        gridsize.text = "50,50"  # 50 pixels per grid square
        
        gridoffset = ET.SubElement(image_data, 'gridoffset')
        gridoffset.text = "0,0"  # No offset
        
        # Name (display name in FG)
        name = ET.SubElement(image_elem, 'name')
        name.set('type', 'string')
        name.text = image['name']
        
        return image_elem
    
    def generate(self):
        """Generate the complete <image> section"""
        if not self.loader.images:
            return None
        
        if self.verbose:
            print(f"  Generating {len(self.loader.images)} images...")
        
        # Create root image element
        image_root = ET.Element('image')
        
        for image in self.loader.images:
            image_elem = self.create_image(image)
            image_root.append(image_elem)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.images)} images")
        
        return image_root
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
