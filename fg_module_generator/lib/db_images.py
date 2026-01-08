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
        
        # Filename (display name)
        n = ET.SubElement(layer, 'n')
        filename = image.get('file', 'unknown.jpg')
        n.text = filename
        
        # Bitmap path (relative to module)
        bitmap = ET.SubElement(layer, 'bitmap')
        bitmap.text = f"images/{filename}"
        
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
