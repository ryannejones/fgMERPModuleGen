"""
Module Packager - Create .mod file from XML and resources
"""

import os
import shutil
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

class ModulePackager:
    def __init__(self, loader, verbose=False):
        self.loader = loader
        self.verbose = verbose
        self.temp_dir = None
    
    def create_definition_xml(self):
        """Create definition.xml with module metadata"""
        root = ET.Element('root')
        root.set('version', '5')
        root.set('dataversion', '20250919')
        root.set('release', '2.3|CoreRPG:7')
        
        # Name (internal name)
        name = ET.SubElement(root, 'name')
        name.text = self.loader.config['name']
        
        # Display name
        displayname = ET.SubElement(root, 'displayname')
        displayname.text = self.loader.config['display_name']
        
        # Author
        author = ET.SubElement(root, 'author')
        author.text = self.loader.config['author']
        
        # Category (optional)
        if 'category' in self.loader.config:
            category = ET.SubElement(root, 'category')
            category.text = self.loader.config['category']
        
        # Ruleset
        ruleset = ET.SubElement(root, 'ruleset')
        ruleset.text = 'RolemasterClassic'
        
        return root
    
    def xml_to_string(self, root):
        """Convert XML element to formatted string"""
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t", encoding='utf-8').decode('utf-8')
    
    def create_temp_directory(self):
        """Create temporary directory for module assembly"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix='fg_module_'))
        if self.verbose:
            print(f"  Created temp directory: {self.temp_dir}")
        return self.temp_dir
    
    def copy_images(self):
        """Copy images directory and thumbnail.png to temp directory"""
        something_copied = False
        
        # Copy thumbnail.png if it exists (goes in root of module)
        source_thumbnail = self.loader.module_dir / 'thumbnail.png'
        if source_thumbnail.exists():
            dest_thumbnail = self.temp_dir / 'thumbnail.png'
            shutil.copy2(source_thumbnail, dest_thumbnail)
            something_copied = True
            if self.verbose:
                print("  [OK] Copied thumbnail.png")
        
        # Copy ALL files from images/ directory (FG auto-imports them)
        source_images = self.loader.module_dir / 'images'
        if source_images.exists() and source_images.is_dir():
            dest_images = self.temp_dir / 'images'
            dest_images.mkdir(exist_ok=True)
            
            # Copy all image files
            copied = 0
            for source_file in source_images.rglob('*'):
                if source_file.is_file():
                    # Preserve directory structure
                    rel_path = source_file.relative_to(source_images)
                    dest_file = dest_images / rel_path
                    
                    # Create subdirectories if needed
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(source_file, dest_file)
                    copied += 1
            
            if copied > 0:
                something_copied = True
                if self.verbose:
                    print(f"  [OK] Copied {copied} image files")
        
        if not something_copied and self.verbose:
            print("  [SKIP] No images to copy")
        
        return something_copied
    
    def copy_tokens(self):
        """Copy tokens directory to temp directory"""
        source_tokens = self.loader.module_dir / 'tokens'
        
        if not source_tokens.exists() or not source_tokens.is_dir():
            if self.verbose:
                print("  [SKIP] No tokens to copy")
            return False
        
        dest_tokens = self.temp_dir / 'tokens'
        dest_tokens.mkdir(exist_ok=True)
        
        # Copy all token files
        copied = 0
        for source_file in source_tokens.rglob('*'):
            if source_file.is_file():
                # Preserve directory structure
                rel_path = source_file.relative_to(source_tokens)
                dest_file = dest_tokens / rel_path
                
                # Create subdirectories if needed
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(source_file, dest_file)
                copied += 1
        
        if copied > 0:
            if self.verbose:
                print(f"  [OK] Copied {copied} token files")
            return True
        
        if self.verbose:
            print("  [SKIP] No tokens to copy")
        return False

    def write_generated_tokens(self):
        """
        Write auto-generated letter token PNGs into tokens/ inside the temp module folder.
        NPCGenerator records what it needs in loader.generated_tokens[token_path] = initial
        """
        gen = getattr(self.loader, "generated_tokens", None)
        if not gen:
            if self.verbose:
                print("  [SKIP] No generated tokens to write")
            return False

        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as e:
            raise RuntimeError(
                "Auto token generation requires Pillow. Install it with: pip install pillow"
            ) from e

        wrote = 0
        for token_path, letter in gen.items():
            out_path = self.temp_dir / token_path  # e.g. tokens/id-00001.png
            out_path.parent.mkdir(parents=True, exist_ok=True)

            size = 100
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            pad = 4
            draw.ellipse((pad, pad, size - pad, size - pad), fill=(60, 60, 60, 255))

            text = (letter or "?")[:1].upper()
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 56)
            except Exception:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(((size - tw) / 2, (size - th) / 2 - 2), text, font=font, fill=(255, 255, 255, 255))

            img.save(out_path, "PNG")
            wrote += 1

        if self.verbose:
            print(f"  [OK] Wrote {wrote} generated token files")
        return wrote > 0

    def create_zip(self, output_path):
        """Create .mod file (zip archive) from temp directory"""
        
        if self.verbose:
            print(f"  Creating .mod archive...")
        
        # Create zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all files from temp directory
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.temp_dir).as_posix()
                    zf.write(file_path, arcname)
        
        if self.verbose:
            print(f"  [OK] Created .mod archive")
        
        return True
    
    def cleanup(self):
        """Remove temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            if self.verbose:
                print(f"  Cleaned up temp directory")
    
    def package(self, db_xml, output_dir=None, output_filename=None):
        """
        Package module as .mod file
        
        Args:
            db_xml: ET.Element - The complete db.xml root element
            output_dir: Path to output directory (default: ./output)
            output_filename: Output filename (default: {module_name}.mod)
        
        Returns:
            Path to created .mod file
        """
        
        try:
            # Determine output path
            if output_dir is None:
                output_dir = Path.cwd() / 'output'
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if output_filename is None:
                output_filename = f"{self.loader.config['name']}.mod"
            
            output_path = output_dir / output_filename
            
            if self.verbose:
                print(f"\nPackaging module: {self.loader.config['display_name']}")
                print(f"Output: {output_path}")
                print()
            
            # Create temp directory
            self.create_temp_directory()
            
            # Create definition.xml
            if self.verbose:
                print("  Creating definition.xml...")
            
            definition_root = self.create_definition_xml()
            definition_xml = self.xml_to_string(definition_root)
            
            definition_path = self.temp_dir / 'definition.xml'
            with open(definition_path, 'w', encoding='utf-8') as f:
                f.write(definition_xml)
            
            if self.verbose:
                print("  [OK] Created definition.xml")
            
            # Write db.xml
            if self.verbose:
                print("  Creating db.xml...")
            
            db_xml_string = self.xml_to_string(db_xml)
            
            db_path = self.temp_dir / 'db.xml'
            with open(db_path, 'w', encoding='utf-8') as f:
                f.write(db_xml_string)
            
            if self.verbose:
                print("  [OK] Created db.xml")
            
            # Copy images
            self.copy_images()
            
            # Copy tokens
            self.copy_tokens()
           
            # Write tokens
            self.write_generated_tokens()
 
            # Create .mod file (zip)
            self.create_zip(output_path)
            
            # Cleanup
            self.cleanup()
            
            return output_path
        
        except Exception as e:
            # Cleanup on error
            if self.temp_dir:
                self.cleanup()
            raise e
