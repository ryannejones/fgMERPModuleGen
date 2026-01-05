# Fantasy Grounds Module Generator - Phases 1-3

## What's Implemented

[DONE] **Phase 1: Core Infrastructure**
- Command-line argument parsing
- YAML file loading with error handling
- Module configuration validation
- Structured error/warning logging

[DONE] **Phase 2: Reference Library**
- Creature/NPC library loading (creature_npc_library.json)
- Weapons reference loading (arms_law_weapons.json)
- Items reference loading (character_law_*.json)
- Lookup functions for all reference data

[DONE] **Phase 3: Validation System**
- Validate creature references (library + custom)
- Validate weapon references
- Validate cross-references between YAML files
- Build name→ID mappings for XML generation
- Comprehensive error reporting

## Files Included

```
fg_module_generator/
├── fg_generator.py          # Main entry point
├── lib/
│   ├── __init__.py          # Package init
│   ├── loader.py            # YAML file loader (177 lines)
│   ├── library.py           # Reference data loader (175 lines)
│   └── validator.py         # Validation system (170 lines)  
└── reference_data/
    ├── creature_npc_library.json
    ├── arms_law_weapons.json
    └── character_law_*.json (7 files)
```

## Usage

### Validate Chapter 6 Module

```bash
python fg_generator.py path/to/chapter6/ --validate-only
```

### Expected Output

```
============================================================
Fantasy Grounds Module Generator
============================================================

Phase 1: Loading Reference Library
------------------------------------------------------------
  [OK] creature_npc_library.json: 8 creatures, 7 NPCs
  [OK] arms_law_weapons.json: 75 weapons
  [OK] Character Law items: 299 items

Phase 2: Loading Module Files
------------------------------------------------------------
  [OK] module.yaml: Skauril's Army - Assault on the Elves
  [OK] stories.yaml: 18 entries
  [OK] encounters.yaml: 6 encounters
  [OK] npcs.yaml: 4 custom NPCs
  [OK] items.yaml: 5 items
  [OK] parcels.yaml: 6 parcels

Phase 3: Validating Module
------------------------------------------------------------
  [OK] Validated 6 encounters
  [OK] Validated 18 stories
  [OK] Validated 4 custom NPCs

============================================================
Validation Summary
============================================================
Module: Skauril's Army - Assault on the Elves
Author: Your Name

Content:
  Stories:     18
  Encounters:  6
  Custom NPCs: 4
  Items:       5
  Parcels:     6
  Images:      0

References:
  Creatures from library: 18
  Custom creatures:       4

[OK] Validation successful - no errors or warnings

[OK] Validation complete (--validate-only mode)
```

## What It Does

### 1. Loads Reference Data
- Reads all JSON reference files
- Builds lookup dictionaries
- Reports what's available

### 2. Loads Module YAML Files
- Validates YAML syntax
- Checks required fields
- Reports what was found

### 3. Validates Everything
- **Encounters:** Every creature reference must exist
- **Stories:** Every link must point to valid content
- **NPCs:** Every weapon must exist or have attack table
- **Parcels:** Every item reference must exist
- **Images:** Every image file must exist on disk

### Error Reporting Example

```
ERROR: Encounter '6.5.03 - Road Crew' references unknown creature: 'Super Orc'
  → Add to npcs.yaml or check spelling

ERROR: Story '6.1.02' links to unknown encounter: 'Orc Battle'
  → Available encounters: 6.5.02 - Bridge Crew, 6.5.03 - Road Crew
```

## Testing

### Test with Chapter 6 (included)

```bash
# Extract the archive
tar xzf fg_module_generator_phases1-3.tar.gz
cd fg_module_generator

# Run validation on test data
python fg_generator.py ../test_chapter6/ --validate-only
```

## What's NOT Implemented (Yet)

[WARN] **Phase 4:** Battle XML generation  
[WARN] **Phase 5:** Story XML generation  
[WARN] **Phase 6:** NPC XML generation  
[WARN] **Phase 7:** Items/Parcels XML generation  
[WARN] **Phase 8:** Images XML generation  
[WARN] **Phase 9:** Library integration (db.xml assembly)  
[WARN] **Phase 10:** .mod packaging  
[WARN] **Phase 11:** Update mode  

## Next Steps

To complete the generator, implement Phases 4-11:

1. **Phase 4 (250 lines):** Generate `<battle>` XML from encounters.yaml
2. **Phase 5 (300 lines):** Generate `<encounter>` (stories) XML from stories.yaml
3. **Phase 6 (350 lines):** Generate `<npc>` XML from npcs.yaml
4. **Phase 7 (250 lines):** Generate `<item>` and `<treasureparcels>` XML
5. **Phase 8 (150 lines):** Generate `<image>` XML
6. **Phase 9 (200 lines):** Assemble complete db.xml with library section
7. **Phase 10 (200 lines):** Package as .mod file
8. **Phase 11 (300 lines):** Update mode for existing modules

See `IMPLEMENTATION_PLAN.md` for detailed specifications.

## Code Quality

- [DONE] Clean separation of concerns (loader/library/validator)
- [DONE] Comprehensive error handling
- [DONE] User-friendly error messages
- [DONE] Verbose mode for debugging
- [DONE] Type hints ready (can add if desired)
- [DONE] Documented functions
- [DONE] ~520 lines total (well under budget)

## Dependencies

- Python 3.6+
- PyYAML (`pip install pyyaml`)
- Standard library only otherwise

## License

Part of the Fantasy Grounds Module Generator project.

## Notes

This implementation validates the entire YAML structure and all cross-references WITHOUT generating any XML. This ensures that when XML generation is added, we know the input data is valid.

The validation catches:
- Missing creatures/NPCs
- Missing weapons
- Broken links between content
- Missing image files
- Invalid YAML syntax
- Missing required fields

This solid foundation makes Phases 4-11 straightforward - just XML generation and packaging!
