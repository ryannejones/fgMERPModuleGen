# TODO - Fantasy Grounds Module Generator

## High Priority

### 1. ⚠️ REVISIT: Spell System
**Status:** Needs review by someone familiar with MERP/Rolemaster magic

**What We Have:**
- 162 spell list references extracted (54 per realm)
- NPCs have empty `spells` sections
- Spell lists reference Spell Law module

**Questions to Answer:**
- How do spell lists actually work in MERP/Rolemaster?
- Do NPCs need pre-populated spell lists, or is empty correct?
- Are individual spells part of spell lists, or separate?
- How do GMs typically assign spells to NPCs in Fantasy Grounds?
- Should users be able to specify spells in YAML, or only in FG?

**Current Approach:**
- Leave spell sections empty (GMs add in FG)
- Optional: Allow users to specify spell lists in YAML
- Spell list references available in `spell_references.json`

**Action Needed:**
- Test with actual MERP/Rolemaster player who uses magic
- Verify spell list references work correctly in Fantasy Grounds
- Determine if current approach matches actual gameplay

**Files:**
- `/mnt/user-data/outputs/spell_references.json`
- `/mnt/user-data/outputs/SPELLS_REFERENCE_GUIDE.md`

---

## Medium Priority

### 2. Smart Partial Matching for Failed Lookups
**Status:** Not started

**Feature**: When an NPC/item isn't found, offer alternatives based on partial word matches

**Examples**:
```
User requests: "Orc Scout"
Not found in library.

Found NPCs containing "Orc":
  1. Orc (non-combatant)     - Level 1,  Hits 15,  OB 13
  2. Orc, Lesser             - Level 2,  Hits 50,  OB 40
  3. Orc, Greater            - Level 4,  Hits 70,  OB 80
  4. Orc (leader)            - Level 6,  Hits 75,  OB 60
  5. Orc (commander)         - Level 10, Hits 110, OB 90
  
Select number (or press Enter to skip): _

---

User requests: "Radish"
Not found in library.

Found items containing "Radish":
  1. Great Radish
  
Use this item? (y/n): _

---

User requests: "Wolf Pup"
Not found in library.

Found NPCs containing "Wolf":
  1. Wolf - Level 3, Hits 30, OB 45
  
Use as base for custom NPC? (y/n): _
```

**IMPORTANT**: When displaying NPC options, always show Level, Hits, and OB to help users make informed decisions about which variant to use.

**Implementation**:
- Extract significant words from failed query (ignore articles, etc.)
- Search library for entries containing ANY of those words
- Present numbered list of matches
- Allow selection by number
- Works for compound names in either direction:
  - "Orc Scout" finds "Orc (leader)", "Orc (commander)", etc.
  - "Radish" finds "Great Radish"
  - "Scout" finds entries with Scout (if any exist)

**Benefits**:
- Helps users discover available variants
- Works regardless of word order
- Reduces YAML trial-and-error
- Makes library more discoverable
- Natural workflow for partial/compound names

### 3. YAML Schema/Templates
**Status:** Not started

**Need to create:**
- Example YAML files for users to follow
- Schema documentation
- Validation rules
- Sample encounters, NPCs, items

**Files needed:**
- `module_template.yaml` - Full module example
- `encounter_template.yaml` - Encounter examples
- `npc_template.yaml` - NPC examples
- `item_template.yaml` - Item examples
- `YAML_SCHEMA.md` - Complete schema documentation

### 4. Pre-Rolled Random Encounters
**Status:** Not started

**Feature**: Generate pre-rolled random encounters with full stat blocks

**Why**: Random encounter tables require GMs to:
1. Roll on table to determine encounter
2. Look up creatures in rulebook
3. Manually create NPCs in FG
4. Determine treasure
5. Repeat for each possible encounter

**Solution**: Pre-generate all possible random encounters in module

**Example YAML**:
```yaml
random_encounters:
  - table: "Mirkwood Random Encounters"
    entries:
      - roll: "01-10"
        name: "Spider Patrol"
        npcs:
          - name: "Giant Spider"
            count: "1d6"
            faction: foe
        treasure:
          coins:
            GP: "2d10"
      
      - roll: "11-25"
        name: "Orc Band"
        npcs:
          - name: "Orc, Lesser"
            count: "2d6"
          - name: "Orc (leader)"
            count: 1
        treasure:
          parcel: "Orc Band Loot"
      
      - roll: "26-40"
        name: "Peaceful Encounter"
        description: "Deer grazing, no combat"
```

**Implementation**:
- Generator creates encounter for EACH table entry
- Roll ranges tracked for GM reference
- Variable counts (1d6, 2d6) handled as text or pre-rolled options
- Optional treasure per encounter
- All pre-generated in module (no lookup needed)

**Benefits**:
- GM rolls once, picks pre-made encounter
- No manual NPC creation
- Consistent treasure
- Fast random encounters during play

**Priority**: Medium - Very useful but not critical for basic module generation

---

### 5. XML Generation
**Status:** Not started

**Need to create:**
- JSON → Fantasy Grounds XML converter
- Handle NPCs with full stat blocks
- Handle items with full stat blocks
- Handle encounters
- Handle story/chapters
- Module metadata (name, author, version)

**Files needed:**
- `xml_generator.py` - Main XML generation
- `npc_to_xml.py` - NPC conversion
- `item_to_xml.py` - Item conversion
- `encounter_to_xml.py` - Encounter conversion

---

### 4. Module Structure
**Status:** Not started

**Need to define:**
- How are encounters organized?
- How is story structure handled?
- Chapter/section organization
- Links between encounters and NPCs

---

## Low Priority

### 5. Images and Tokens
**Status:** Not started

**Need to support:**
- NPC/creature tokens (portraits and battle tokens)
- Map images
- Handout images
- Image embedding in modules
- Image file formats (PNG, JPG)
- Image references in XML

**Questions:**
- How are images referenced in Fantasy Grounds modules?
- Token size requirements?
- Where should users place image files?
- Should images be embedded or referenced?
- Default tokens for creatures without custom art?

**Potential approach:**
- Accept image directory in YAML
- Copy images into module
- Generate proper XML references
- Support both embedded and external images

---

### 6. Tables
**Status:** Not started

**Questions:**
- Are attack/critical tables needed in modules?
- Or do users already have them from rulebooks?
- Any module-specific tables needed?

---

### 7. Treasure Parcels
**Status:** Not started

**Need to determine:**
- Are treasure parcels different from items?
- Do they need special handling?
- How do they work in Fantasy Grounds?

---

## Completed ✅

### Item Reference System ✅
- **✅ Research completed**: FG copies item data (not references) when added to character inventory
- **✅ Design decision**: Use references within module, FG handles copying
- **✅ Implementation**: NPCs reference module items, parcels reference module items
- **✅ Single point of truth**: Items defined once in module
- **✅ Character portability**: Items copied to character, work in any campaign
- **Sources**: Fantasy Grounds forums confirm DB.copyNode behavior

### NPCs/Creatures Database
- ✅ 715 entries extracted with all fields
- ✅ Source priority system (CL > AL > C&T)
- ✅ Python library with search/copy functions

### Items Database
- ✅ 1,257 entries extracted with all fields
- ✅ Source priority system
- ✅ Python library with search/copy functions

### Matching System
- ✅ Profession mappings (Animist → Pure Channeling Spell User, etc.)
- ✅ Creature aliases (Warg → Wolf, etc.)
- ✅ Item aliases (Sword → Broadsword, etc.)
- ✅ Fuzzy matching with 80%+ threshold
- ✅ Default level 5 for leveled NPCs
- ✅ Level rounding to nearest available

### Skills Reference
- ✅ 80 skills extracted
- ✅ Skills already properly referenced in NPCs
- ✅ Points to Character Law skill definitions

### Spell Lists Reference
- ✅ 162 spell lists extracted (54 per realm)
- ✅ Reference table created
- ⚠️ Needs gameplay testing (see item #1)

### Design Decisions
- ✅ Use full stat blocks (not references)
- ✅ Self-contained modules
- ✅ No dependencies required
- ✅ All documented

---

## Files Status

### Complete and Ready
- `npcs_and_creatures_complete.json` (5.2 MB)
- `npc_creature_library_complete.py`
- `items_complete.json` (4.34 MB)
- `item_library_complete.py`
- `npc_creature_item_mappings.yaml`
- `entity_matcher.py`
- `skill_references.json`
- `spell_references.json`
- All documentation files

### Needed
- YAML templates/examples
- XML generation scripts
- Module assembly script
- Main command-line interface

---

## Next Steps

1. **TEST SPELLS** - Find MERP/Rolemaster magic user to validate spell system
2. **Create YAML templates** - Give users examples to follow
3. **Build XML generator** - Convert JSON data to Fantasy Grounds XML
4. **Build module assembler** - Put everything together into .mod file
5. **Create CLI tool** - Main script to run the whole process

---

## Questions for Later

- How should errors be reported to users?
- How to handle module versioning?
- Should there be a validation mode before generation?
- How to handle module updates/patches?

---

**Last Updated:** 2026-01-07
