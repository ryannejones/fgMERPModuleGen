#!/usr/bin/env python3
"""
Test script for battle XML generation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.loader import ModuleLoader
from lib.library import ReferenceLibrary
from lib.validator import ModuleValidator
from lib.db_battles import BattleGenerator

def main():
    # Load test data
    test_dir = Path(__file__).parent.parent / 'test_chapter6'
    
    print("Loading test data from:", test_dir)
    print()
    
    # Load library
    library = ReferenceLibrary(verbose=True)
    library.load_all()
    print()
    
    # Load module
    loader = ModuleLoader(test_dir, verbose=True)
    loader.load_all()
    print()
    
    # Validate
    validator = ModuleValidator(loader, library, verbose=True)
    validator.validate_all()
    print()
    
    # Generate battle XML
    print("=" * 60)
    print("Generating Battle XML")
    print("=" * 60)
    print()
    
    battle_gen = BattleGenerator(loader, library, verbose=True)
    battle_xml = battle_gen.generate()
    
    if battle_xml:
        xml_string = battle_gen.to_xml_string(battle_xml)
        
        # Write to file
        output_file = Path(__file__).parent / 'test_battles.xml'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        print(f"\n[OK] Battle XML written to: {output_file}")
        print("\nFirst 50 lines of output:")
        print("-" * 60)
        
        lines = xml_string.split('\n')
        for line in lines[:50]:
            print(line)
        
        if len(lines) > 50:
            print(f"\n... ({len(lines) - 50} more lines)")
    else:
        print("[WARN] No battles to generate")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
