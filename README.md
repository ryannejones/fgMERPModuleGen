# Fantasy Grounds Module Generator v0.11

**Version**: 0.11  
**Date**: 2026-01-07  
**Status**: Pre-Release / Development

Complete Fantasy Grounds module generator with intelligent NPC/item matching, compound name handling, and full stat block generation.

## What's New in v0.11

- ✅ Compound name matching documented (e.g., "Orc Scout" won't match "Scout")
- ✅ Default level fixed: 4 → 5 (level 4 doesn't exist in library)
- ✅ Smart partial matching feature planned for next version
- ✅ Comprehensive matching behavior documentation
- ✅ CHANGELOG added

## Quick Start

```bash
# Test the library
python3 test_library.py

# Generate a module
python3 fg_generator.py examples/test_chapter6/ -v
```

## Features

- **715 NPCs/Creatures** with complete stat blocks
- **1,257 Items** with complete data
- **80 Skills** with Character Law references
- **162 Spell Lists** across 3 realms
- **Intelligent Matching**: Profession mappings, aliases, fuzzy matching
- **Source Priority**: Character Law > Arms Law > Creatures & Treasures

## Directory Structure

```
fg_module_generator_v0.11/
├── fg_generator.py          # Main script
├── lib/                     # Core libraries
│   ├── library.py          # Integrated reference library
│   ├── npc_creature_library_complete.py
│   ├── item_library_complete.py
│   ├── entity_matcher.py
│   ├── db_npcs.py          # NPC XML generator
│   ├── db_items.py         # Item XML generator
│   └── ... (other modules)
├── data/                    # Complete databases (13+ MB)
│   ├── npcs_and_creatures_complete.json
│   ├── items_complete.json
│   ├── skill_references.json
│   └── spell_references.json
├── examples/                # Example YAML files
│   └── test_chapter6/
└── docs/                    # Documentation
```

## Documentation

- `README.md` - This file
- `docs/TODO.md` - Roadmap and planned features
- `docs/COMPOUND_NAME_MATCHING.md` - How matching works
- `docs/MATCHING_SYSTEM_GUIDE.md` - Matching system details
- `docs/SKILLS_REFERENCE_GUIDE.md` - Skills documentation
- `docs/SPELLS_REFERENCE_GUIDE.md` - Spell lists documentation

## Status

- ✅ Core library integration complete
- ✅ Matching system working
- ✅ Test script passing
- ⏳ End-to-end testing needed
- ⏳ XML generation validation needed

## Next Steps

See `docs/TODO.md` for complete roadmap.

Priority items:
1. Smart partial matching for failed lookups
2. End-to-end module generation testing
3. XML output validation

## Version History

- **v0.11** (2026-01-07): Compound name matching documented, default level fixed
- **v0.10** (2026-01-07): Complete data extraction, library integration
- **v10_FINAL** (previous): Initial version

## License

For MERP/Rolemaster use only. Respects ICE copyright.
