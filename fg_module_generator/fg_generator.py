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
        print(f"  [OK] Generated battle XML for {len(loader.encounters)} encounters")
    else:
        print("  [WARN] No encounters to generate")
    print()
    
    # TODO: Phase 5-10 - Story XML, NPC XML, Items, Parcels, Images, Packaging
    print("[WARN] Full module generation not yet implemented")
    print("  Battle XML generated successfully")
    print("  Still needed: Stories, NPCs, Items, Parcels, Images, Packaging")
    print("  Implementation: Phases 5-10 (coming next)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
