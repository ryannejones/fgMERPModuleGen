#!/usr/bin/env python3
"""
Test script for all XML generation phases (4-8)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.loader import ModuleLoader
from lib.library import ReferenceLibrary
from lib.validator import ModuleValidator
from lib.db_battles import BattleGenerator
from lib.db_encounters import EncounterGenerator
from lib.db_npcs import NPCGenerator
from lib.db_items import ItemGenerator
from lib.db_images import ImageGenerator

def save_xml(xml_root, generator, filename):
    """Save XML to file"""
    if xml_root is None:
        print(f"  [SKIP] {filename} - no content")
        return False
    
    xml_string = generator.to_xml_string(xml_root)
    output_file = Path(__file__).parent / filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"  [OK] {filename}")
    return True

def main():
    # Load test data
    test_dir = Path(__file__).parent.parent / 'test_chapter6'
    
    print("=" * 60)
    print("XML Generation Test - Phases 4-8")
    print("=" * 60)
    print()
    
    # Load library
    print("Loading reference library...")
    library = ReferenceLibrary(verbose=False)
    library.load_all()
    
    # Load module
    print("Loading module files...")
    loader = ModuleLoader(test_dir, verbose=False)
    loader.load_all()
    
    # Validate
    print("Validating...")
    validator = ModuleValidator(loader, library, verbose=False)
    if not validator.validate_all():
        print("\n[ERROR] Validation failed")
        validator.print_errors()
        return 1
    
    print()
    print("=" * 60)
    print("Generating XML Files")
    print("=" * 60)
    print()
    
    # Phase 4: Battles
    print("Phase 4: Battles")
    battle_gen = BattleGenerator(loader, library, verbose=False)
    battle_xml = battle_gen.generate()
    save_xml(battle_xml, battle_gen, 'test_battles.xml')
    print()
    
    # Phase 5: Stories (Encounters)
    print("Phase 5: Stories (Encounters)")
    encounter_gen = EncounterGenerator(loader, library, verbose=False)
    encounter_xml = encounter_gen.generate()
    save_xml(encounter_xml, encounter_gen, 'test_encounters.xml')
    print()
    
    # Phase 6: NPCs
    print("Phase 6: Custom NPCs")
    npc_gen = NPCGenerator(loader, library, verbose=False)
    npc_xml = npc_gen.generate()
    save_xml(npc_xml, npc_gen, 'test_npcs.xml')
    print()
    
    # Phase 7: Items and Parcels
    print("Phase 7: Items and Parcels")
    item_gen = ItemGenerator(loader, library, verbose=False)
    
    item_xml = item_gen.generate_items()
    save_xml(item_xml, item_gen, 'test_items.xml')
    
    parcel_xml = item_gen.generate_parcels()
    save_xml(parcel_xml, item_gen, 'test_parcels.xml')
    print()
    
    # Phase 8: Images
    print("Phase 8: Images")
    image_gen = ImageGenerator(loader, library, verbose=False)
    image_xml = image_gen.generate()
    if image_xml is None:
        print("  [SKIP] test_images.xml - no images in module")
    else:
        save_xml(image_xml, image_gen, 'test_images.xml')
    print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Battles:    {len(loader.encounters)} encounters")
    print(f"Stories:    {len(loader.stories)} entries")
    print(f"NPCs:       {len(loader.npcs)} custom")
    print(f"Items:      {len(loader.items)} items")
    print(f"Parcels:    {len(loader.parcels)} parcels")
    print(f"Images:     {len(loader.images)} images")
    print()
    print("[OK] All XML files generated successfully")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
