#!/usr/bin/env python3
"""
Fantasy Grounds Module Generator
Generates Fantasy Grounds .mod files from YAML input files
"""

import sys
import argparse
from pathlib import Path

# Import our library modules
from lib.loader import ModuleLoader
from lib.validator import ModuleValidator
from lib.library import ReferenceLibrary

def main():
    parser = argparse.ArgumentParser(
        description='Generate Fantasy Grounds modules from YAML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate new module:
    python fg_generator.py chapter6/
  
  Validate only (don't generate):
    python fg_generator.py chapter6/ --validate-only
  
  Update existing module:
    python fg_generator.py chapter6/ --update existing_module.mod
  
  Specify output directory:
    python fg_generator.py chapter6/ --output ./my_modules/
        """
    )
    
    parser.add_argument('module_dir', 
                       help='Directory containing module YAML files')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate, do not generate module')
    parser.add_argument('--update', metavar='MODFILE',
                       help='Update existing .mod file with new content')
    parser.add_argument('--output', metavar='DIR',
                       help='Output directory (default: ./output)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
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
        print("\n❌ Failed to load reference library")
        return 1
    print()
    
    # Phase 2: Load module files
    print("Phase 2: Loading Module Files")
    print("-" * 60)
    loader = ModuleLoader(module_dir, verbose=args.verbose)
    if not loader.load_all():
        print("\n❌ Failed to load module files")
        loader.print_errors()
        return 1
    print()
    
    # Phase 3: Validate
    print("Phase 3: Validating Module")
    print("-" * 60)
    validator = ModuleValidator(loader, library, verbose=args.verbose)
    if not validator.validate_all():
        print("\n❌ Validation failed")
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
        print("✓ Validation complete (--validate-only mode)")
        return 0
    
    # TODO: Phase 4+ - XML Generation and Packaging
    print("⚠ XML Generation not yet implemented")
    print("  Module validated successfully but not generated")
    print("  Implementation: Phases 4-10 (coming next)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
