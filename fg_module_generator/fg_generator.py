#!/usr/bin/env python3
"""
Fantasy Grounds Module Generator
Generates Fantasy Grounds .mod files from YAML input files
"""

import sys
import argparse
from pathlib import Path

from lib.loader import ModuleLoader
from lib.validator import ModuleValidator
from lib.library import ReferenceLibrary
from lib.db_battles import BattleGenerator
from lib.db_stories import StoryGenerator
from lib.db_npcs import NPCGenerator
from lib.db_items import ItemGenerator
from lib.db_images import ImageGenerator
from lib.db_generator import DBGenerator
from lib.packager import ModulePackager

def main():
    parser = argparse.ArgumentParser(
        description='Generate Fantasy Grounds modules from YAML files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('module_dir', help='Directory containing module YAML files')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not generate module')
    parser.add_argument('--update', metavar='MODFILE', help='Update existing .mod file with new content')
    parser.add_argument('--output', metavar='DIR', help='Output directory (default: ./output)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate module directory exists
    module_dir = Path(args.module_dir)
    if not module_dir.exists():
        print(f"ERROR: Module directory not found: {module_dir}")
        return 1
    
    if not module_dir.is_dir():
        print(f"ERROR: Not a directory: {module_dir}")
        return 1
    
    # Print header
    print("=" * 60)
    print("Fantasy Grounds Module Generator")
    print("=" * 60)
    print()
    
    # Phase 1: Load reference library
    print("Phase 1: Loading Reference Library")
    print("-" * 60)
    library = ReferenceLibrary(verbose=args.verbose)
    if not library.load_all():
        print("\nERROR: Failed to load reference library")
        return 1
    print()
    
    # Phase 2: Load module files
    print("Phase 2: Loading Module Files")
    print("-" * 60)
    loader = ModuleLoader(module_dir, verbose=args.verbose)
    if not loader.load_all():
        print("\nERROR: Failed to load module files")
        loader.print_errors()
        return 1
    print()
    
    # Phase 3: Validate
    print("Phase 3: Validating Module")
    print("-" * 60)
    validator = ModuleValidator(loader, library, verbose=args.verbose)
    if not validator.validate_all():
        print("\nERROR: Validation failed")
        validator.print_errors()
        return 1
    print()
    
    # Summary
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)
    validator.print_summary()
    print()
    
    if args.validate_only:
        print("[OK] Validation complete (--validate-only mode)")
        return 0
    
    # Phase 4: Generate Battle XML
    print("Phase 4: Generating Battle XML")
    print("-" * 60)
    battle_gen = BattleGenerator(loader, library, verbose=args.verbose)
    battle_xml = battle_gen.generate()
    
    if battle_xml is not None:
        print(f"  [OK] Generated {len(loader.encounters)} battles")
    else:
        print("  [SKIP] No encounters to generate")
    print()
    
    # Phase 5: Generate Story XML  
    print("Phase 5: Generating Story XML")
    print("-" * 60)
    story_gen = StoryGenerator(loader, library, verbose=args.verbose)
    story_xml = story_gen.generate()
    
    if story_xml is not None:
        print(f"  [OK] Generated {len(loader.stories)} stories")
    else:
        print("  [SKIP] No stories to generate")
    print()
    
    # Phase 6: Generate NPC XML
    print("Phase 6: Generating NPC XML")
    print("-" * 60)
    npc_gen = NPCGenerator(loader, library, verbose=args.verbose)
    npc_xml = npc_gen.generate()
    
    if npc_xml is not None:
        print(f"  [OK] Generated {len(loader.npcs)} custom NPCs")
    else:
        print("  [SKIP] No custom NPCs to generate")
    print()
    
    # Phase 7: Generate Items and Parcels XML
    print("Phase 7: Generating Items and Parcels XML")
    print("-" * 60)
    item_gen = ItemGenerator(loader, library, verbose=args.verbose)
    
    item_xml = item_gen.generate_items()
    if item_xml is not None:
        print(f"  [OK] Generated {len(loader.items)} items")
    else:
        print("  [SKIP] No items to generate")
    
    parcel_xml = item_gen.generate_parcels()
    if parcel_xml is not None:
        print(f"  [OK] Generated {len(loader.parcels)} parcels")
    else:
        print("  [SKIP] No parcels to generate")
    print()
    
    # Phase 8: Generate Images XML
    print("Phase 8: Generating Images XML")
    print("-" * 60)
    image_gen = ImageGenerator(loader, library, verbose=args.verbose)
    image_xml = image_gen.generate()
    
    if image_xml is not None:
        print(f"  [OK] Generated {len(loader.images)} images")
    else:
        print("  [SKIP] No images to generate")
    print()
    
    # Phase 9: Assemble db.xml
    print("Phase 9: Assembling db.xml")
    print("-" * 60)
    db_gen = DBGenerator(loader, library, verbose=args.verbose)
    db_xml = db_gen.generate(
        battle_xml=battle_xml,
        story_xml=story_xml,
        npc_xml=npc_xml,
        item_xml=item_xml,
        parcel_xml=parcel_xml,
        image_xml=image_xml
    )
    
    if db_xml is not None:
        print("  [OK] Assembled complete db.xml")
    else:
        print("  [ERROR] Failed to assemble db.xml")
        return 1
    print()
    
    # Phase 10: Package module
    print("Phase 10: Packaging Module")
    print("-" * 60)
    
    # Determine output settings
    output_dir = args.output if args.output else './output'
    
    packager = ModulePackager(loader, verbose=args.verbose)
    
    try:
        output_path = packager.package(db_xml, output_dir=output_dir)
        
        print()
        print("=" * 60)
        print("Module Generation Complete!")
        print("=" * 60)
        print(f"Module: {loader.config['display_name']}")
        print(f"Author: {loader.config['author']}")
        print(f"File:   {output_path}")
        print()
        print("Content Summary:")
        print(f"  Battles:    {len(loader.encounters)}")
        print(f"  Stories:    {len(loader.stories)}")
        print(f"  NPCs:       {len(loader.npcs)}")
        print(f"  Items:      {len(loader.items)}")
        print(f"  Parcels:    {len(loader.parcels)}")
        print(f"  Images:     {len(loader.images)}")
        print()
        print("[OK] Module ready to import into Fantasy Grounds!")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to package module: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
