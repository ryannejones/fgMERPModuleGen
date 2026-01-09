# Migration Plan: FINAL → v0.10

## Version History
- **Old version**: "v10_FINAL" (misnamed - not actually final)
- **New version**: **0.10** (pre-release, not ready for production)
- **Future version**: **1.0** (first stable release)

## What Changed Today (Major Improvements)

### 1. Complete Data Extraction
**Old**: Partial data in `reference_data/` directory
- Small JSON files with limited fields
- Incomplete NPC/creature coverage

**New**: Complete databases with ALL fields
- `npcs_and_creatures_complete.json` (5.2 MB, 715 entries)
- `items_complete.json` (7.5 MB, 1,257 entries)
- Every field from source XMLs preserved

### 2. Source Priority System
**Old**: No conflict resolution
**New**: Automatic priority (Character Law > Arms Law > Creatures & Treasures)
- Handles 41 creature duplicates
- Handles 55 item duplicates
- Transparent selection with user override option

### 3. Entity Matching System
**Old**: Direct lookups only
**New**: Multi-strategy matching
- Profession mappings (Animist → Pure Channeling Spell User)
- Creature aliases (Warg → Wolf)
- Fuzzy matching (80%+ similarity)
- Graceful failure with suggestions

### 4. Reference Tables
**New**:
- Skills (80 skills with Character Law references)
- Spell Lists (162 spell lists across 3 realms)

### 5. Design Decision: Full Stat Blocks
**Old**: Unclear approach
**New**: Use complete stat blocks, not references
- Self-contained modules
- No module dependencies
- Fully customizable NPCs

## Migration Tasks

### Phase 1: Update Library System ✅ (Completed Today)
- [x] Extract complete NPC/creature data
- [x] Extract complete item data
- [x] Build priority system
- [x] Create matching system
- [x] Extract skill references
- [x] Extract spell list references
- [x] Document everything

### Phase 2: Integrate With Old Generator (TODO)
- [ ] Replace `lib/library.py` with new library system
- [ ] Update `lib/db_npcs.py` to use complete NPCs
- [ ] Update `lib/db_items.py` to use complete items
- [ ] Integrate `entity_matcher.py` for name resolution
- [ ] Update YAML schema to match new capabilities

### Phase 3: XML Generation Updates (TODO)
- [ ] Ensure full stat blocks are generated
- [ ] Update skill XML generation
- [ ] Add optional spell list support
- [ ] Test XML output with Fantasy Grounds

### Phase 4: Testing & Validation (TODO)
- [ ] Test with existing YAML files (`test_chapter6/`)
- [ ] Validate generated modules
- [ ] Compare old vs new output
- [ ] Fix any regressions

### Phase 5: Documentation (TODO)
- [ ] Update all README files
- [ ] Create YAML templates
- [ ] Document new matching system
- [ ] Migration guide for users

### Phase 6: Versioning & Release (TODO)
- [ ] Set version to 0.10
- [ ] Create changelog
- [ ] Package for distribution
- [ ] Mark known issues

## File Organization

### Keep From Old System
```
fg_module_generator/
├── fg_generator.py           # Main entry point (update imports)
├── lib/
│   ├── loader.py            # YAML loader (keep)
│   ├── validator.py         # Validation (keep)
│   ├── db_generator.py      # Database builder (keep)
│   ├── db_battles.py        # Battle/encounter gen (keep)
│   ├── db_stories.py        # Story gen (keep)
│   ├── db_images.py         # Image handling (keep)
│   └── packager.py          # .mod packager (keep)
└── test_chapter6/           # Test YAML files (keep)
```

### Replace From Old System
```
lib/
├── library.py               # REPLACE with new libraries
├── db_npcs.py              # UPDATE to use complete NPCs
└── db_items.py             # UPDATE to use complete items
```

### Add To New System
```
lib/
├── npc_creature_library.py  # NEW: Complete NPC library
├── item_library.py           # NEW: Complete item library
├── entity_matcher.py         # NEW: Name matching system
└── mappings.yaml             # NEW: Profession/alias mappings

data/
├── npcs_and_creatures_complete.json  # NEW: 715 NPCs
├── items_complete.json               # NEW: 1,257 items
├── skill_references.json             # NEW: 80 skills
└── spell_references.json             # NEW: 162 spell lists
```

### Remove From Old System
```
reference_data/                # DELETE: Replaced by complete data
├── character_law_*.json
├── arms_law_*.json
└── creature_npc_library.json
```

## Integration Strategy

### Step 1: Create v0.10 Structure
```bash
fg_module_generator_v0.10/
├── VERSION.txt              # "0.10"
├── fg_generator.py          # Main script
├── lib/                     # Core libraries
├── data/                    # Complete databases (NEW)
├── examples/                # Example YAML files
└── docs/                    # Documentation
```

### Step 2: Update Imports
Old `lib/library.py`:
```python
class ReferenceLibrary:
    def __init__(self):
        self.npcs = self._load_json('reference_data/character_law_npcs.json')
        # Limited data, incomplete
```

New approach:
```python
from lib.npc_creature_library import CompleteNPCCreatureLibrary
from lib.item_library import CompleteItemLibrary
from lib.entity_matcher import EntityMatcher

class ReferenceLibrary:
    def __init__(self):
        self.npcs = CompleteNPCCreatureLibrary('data/npcs_and_creatures_complete.json')
        self.items = CompleteItemLibrary('data/items_complete.json')
        self.matcher = EntityMatcher(self.npcs, self.items, 'lib/mappings.yaml')
```

### Step 3: Update NPC Generation
Old `lib/db_npcs.py`:
```python
def generate_npc(self, npc_data):
    # Creates reference links (broken approach)
    return f'<link recordname="reference.npcs.{id}@Character Law">'
```

New approach:
```python
def generate_npc(self, npc_data):
    # Match the NPC
    result = self.matcher.match_npc(npc_data['name'], npc_data.get('level'))
    
    if result['found']:
        npc_entry = result['entry']
        # Generate COMPLETE stat block XML
        return self._npc_to_xml(npc_entry)
```

### Step 4: Test & Validate
```bash
# Test with existing YAML
python fg_generator.py test_chapter6/

# Should produce working module with:
# - Complete NPC stat blocks
# - Complete item data
# - Skills with proper references
# - Everything self-contained
```

## Breaking Changes

### For Users
1. **YAML syntax unchanged** - Existing YAML files should work
2. **New matching options** - Can now use aliases (Warg, Scout, etc.)
3. **Spell lists optional** - Can specify in YAML or add in FG

### For Developers
1. **`reference_data/` directory removed** - Use `data/` instead
2. **New library imports** - Update any custom scripts
3. **Matching system required** - All name lookups go through matcher

## Known Issues (v0.10)

### High Priority
1. ⚠️ **Spell system needs validation** - Requires testing by magic user
2. **XML generation not fully updated** - Old code may not handle complete stat blocks

### Medium Priority
3. **Images/tokens not implemented** - On TODO list
4. **YAML schema not documented** - Need templates
5. **Error messages need improvement** - Better user feedback

### Low Priority
6. **Performance not optimized** - Large JSON files load slowly
7. **No GUI** - Command-line only
8. **Limited validation** - Can generate invalid modules

## Success Criteria for v1.0

Before calling it 1.0, we need:
- [ ] All components working end-to-end
- [ ] Generated modules tested in Fantasy Grounds
- [ ] Complete documentation
- [ ] Example YAML files
- [ ] No known critical bugs
- [ ] Spell system validated
- [ ] User testing completed

## Timeline Estimate

- **Phase 2** (Integration): 4-6 hours
- **Phase 3** (XML updates): 2-3 hours
- **Phase 4** (Testing): 2-3 hours
- **Phase 5** (Docs): 2-3 hours
- **Phase 6** (Release): 1 hour

**Total**: ~11-16 hours of work to complete v0.10

## Next Immediate Steps

1. **Copy working files** from old system to new v0.10 structure
2. **Integrate new libraries** (replace library.py)
3. **Update db_npcs.py and db_items.py**
4. **Test with test_chapter6 YAML**
5. **Fix any issues**
6. **Update documentation**

---

**Current Status**: Data extraction complete, integration pending
**Target**: Functional v0.10 with complete data support
**Future**: v1.0 when fully tested and documented
