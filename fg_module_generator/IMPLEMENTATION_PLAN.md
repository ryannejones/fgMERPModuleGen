# Fantasy Grounds Module Generator - Implementation Plan

## Overview
The module generator will be a Python script that reads YAML files and generates Fantasy Grounds .mod files. Estimated size: 2000-2500 lines of code.

## File Structure

```
fg_module_generator/
├── fg_generator.py          # Main script (entry point)
├── lib/
│   ├── __init__.py
│   ├── loader.py            # Load YAML files
│   ├── validator.py         # Validate references
│   ├── xml_generator.py     # Generate XML files
│   ├── db_battles.py        # Generate <battle> XML
│   ├── db_encounters.py     # Generate <encounter> (stories) XML
│   ├── db_npcs.py           # Generate <npc> XML
│   ├── db_items.py          # Generate <item> XML
│   ├── db_parcels.py        # Generate <treasureparcels> XML
│   ├── db_images.py         # Generate <image> XML
│   ├── library.py           # Creature/weapon library lookups
│   ├── packager.py          # Create .mod file
│   └── updater.py           # Update existing modules
└── reference_data/
    ├── creature_npc_library.json
    ├── arms_law_weapons.json
    ├── character_law_*.json
    └── (all reference files)
```

## Implementation Phases

### Phase 1: Core Infrastructure (300 lines)
**File:** `fg_generator.py`, `lib/loader.py`

**Features:**
- Command-line argument parsing
- YAML file loading
- Error/warning logging
- Module configuration validation

**Test:**
```bash
python fg_generator.py chapter6/ --validate-only
```

**Output:**
```
[OK] Loaded module.yaml
[OK] Loaded stories.yaml (18 entries)
[OK] Loaded encounters.yaml (7 encounters)
Module structure valid
```

---

### Phase 2: Reference Library (200 lines)
**File:** `lib/library.py`

**Features:**
- Load creature_npc_library.json
- Load arms_law_weapons.json
- Lookup functions for creatures/NPCs
- Lookup functions for weapons
- Lookup functions for items

**Functions:**
```python
get_creature(name)           # Returns creature stats or None
get_weapon(name)             # Returns weapon data or None
validate_creature_exists(name)
validate_weapon_exists(name)
```

---

### Phase 3: Validation System (300 lines)
**File:** `lib/validator.py`

**Features:**
- Validate all creature references
- Validate all weapon references
- Validate story→encounter links
- Validate story→NPC links
- Validate story→item links
- Validate parcel→item links
- Validate image file existence
- Build name→ID mappings

**Output:**
```
Validating references...
[OK] All creatures found (3 from library, 4 custom)
[OK] All encounters referenced correctly
[OK] All items found
[OK] All image files exist
[OK] Validation complete
```

---

### Phase 4: XML Generation - Battles (250 lines)
**File:** `lib/db_battles.py`

**Features:**
- Generate `<battle>` section
- Look up creature stats from library
- Create NPC list entries
- Handle factions (foe/friend/neutral)
- Handle multiple NPCs of same type

**Input:**
```yaml
- name: "6.5.03 - Road Crew"
  exp: 400
  npcs:
    - creature: "Orc Scout"
      count: 10
```

**Output XML:**
```xml
<battle>
  <id-00001>
    <exp type="number">400</exp>
    <name type="string">6.5.03 - Road Crew</n>
    <npclist>
      <id-00001>
        <count type="number">10</count>
        <faction type="string">foe</faction>
        <link type="windowreference">
          <class>npc</class>
          <recordname>npc.id-00026@Character Law</recordname>
        </link>
      </id-00001>
    </npclist>
  </id-00001>
</battle>
```

---

### Phase 5: XML Generation - Stories (300 lines)
**File:** `lib/db_encounters.py`

**Features:**
- Generate `<encounter>` section (stories)
- Convert section types to XML:
  - `header` → `<h>`
  - `read_aloud` → `<frame>`
  - `gm_notes` → `<p>`
  - `link_*` → `<linklist>`
- Handle line breaks (`\n` → actual breaks)
- Build proper `<formattedtext>`

**Input:**
```yaml
sections:
  - type: header
    text: "Day 1"
  - type: read_aloud
    text: "You see orcs ahead."
  - type: link_encounter
    encounter_name: "6.5.03 - Road Crew"
```

**Output XML:**
```xml
<encounter>
  <id-00001>
    <name type="string">Story Name</n>
    <text type="formattedtext">
      <h>Day 1</h>
      <frame>You see orcs ahead.</frame>
      <linklist>
        <link class="battle" recordname="battle.id-00001">
          Encounter: 6.5.03 - Road Crew
        </link>
      </linklist>
    </text>
  </id-00001>
</encounter>
```

---

### Phase 6: XML Generation - NPCs (350 lines)
**File:** `lib/db_npcs.py`

**Features:**
- Generate `<npc>` section for custom NPCs
- Look up weapon attack tables
- Handle weapons array
- Handle defenses array
- Convert abilities to formatted text

**Input:**
```yaml
- name: "Gardagd"
  level: 7
  hp: 60
  weapons:
    - weapon: "Long Bow"
      ob: 65
```

**Output XML:**
```xml
<npc>
  <id-00001>
    <name type="string">Gardagd</n>
    <level type="number">7</level>
    <hits type="number">60</hits>
    <weapons>
      <id-00001>
        <name type="string">Long Bow</n>
        <ob type="number">65</ob>
        <attacktable>
          <tableid type="string">AMT-07</tableid>
        </attacktable>
      </id-00001>
    </weapons>
  </id-00001>
</npc>
```

---

### Phase 7: XML Generation - Items & Parcels (250 lines)
**File:** `lib/db_items.py`, `lib/db_parcels.py`

**Features:**
- Generate `<item>` section
- Handle item properties (bonuses, special abilities)
- Generate `<treasureparcels>` section
- Mix text items and item references in parcels

---

### Phase 8: XML Generation - Images (150 lines)
**File:** `lib/db_images.py`

**Features:**
- Generate `<image>` section
- Copy image files to images/ folder
- Create proper layer structure

---

### Phase 9: Library Integration (200 lines)
**File:** `lib/xml_generator.py`

**Features:**
- Generate complete db.xml
- Generate library section with all content types
- Proper XML formatting
- Handle module internal name replacement

---

### Phase 10: Packaging (200 lines)
**File:** `lib/packager.py`

**Features:**
- Create working directory
- Write definition.xml
- Write db.xml
- Copy images/ folder
- Zip everything
- Rename to .mod
- Clean up temp files

---

### Phase 11: Update Mode (300 lines)
**File:** `lib/updater.py`

**Features:**
- Extract existing .mod
- Parse existing XML
- Identify highest existing IDs
- Merge new content with existing
- Preserve existing IDs
- Update library section
- Repackage

**Usage:**
```bash
python fg_generator.py chapter6/ --update existing_module.mod
```

**Process:**
1. Extract existing_module.mod
2. Parse to find existing content
3. Find max IDs (stories: id-00018, encounters: id-00007, etc.)
4. Start new IDs from id-00019, id-00008, etc.
5. Add new content to XML
6. Repackage

---

## Testing Strategy

### Unit Tests
- Test each XML generator independently
- Test library lookups
- Test validation

### Integration Tests
- Test with chapter6 YAML files
- Test with minimal module
- Test with complex module

### End-to-End Tests
1. Generate chapter6 module
2. Load in Fantasy Grounds
3. Verify all content appears
4. Test links work
5. Test encounters load properly

---

## Error Handling

### Required Checks:
- [DONE] module.yaml exists and valid
- [DONE] Creature references exist
- [DONE] Weapon references exist  
- [DONE] Cross-references valid
- [DONE] Image files exist
- [DONE] YAML syntax valid
- [DONE] Required fields present

### User-Friendly Messages:
```
ERROR: Encounter '6.5.03 - Road Crew' references unknown creature 'Super Orc'
  → Check creature_npc_library.json or add to npcs.yaml
  
ERROR: Story '6.1.02' links to unknown encounter 'Orc Battle'
  → Available encounters: 6.5.02 - Bridge Crew, 6.5.03 - Road Crew
  
ERROR: Image file not found: images/map.jpg
  → Expected at: /path/to/module/images/map.jpg
```

---

## Recommended Build Order

1. **Start Small:** Get basic module generation working (Phase 1-3)
2. **One Content Type:** Implement battles fully (Phase 4)
3. **Test:** Generate simple encounter, test in FG
4. **Iterate:** Add stories, then NPCs, then items
5. **Final:** Add update mode

**First Milestone:** Generate a working module with just encounters

**Second Milestone:** Add stories with working links

**Third Milestone:** Add custom NPCs

**Fourth Milestone:** Complete all content types

**Fifth Milestone:** Add update mode

---

## File Size Estimates

```
fg_generator.py         ~150 lines   (main entry point)
lib/loader.py           ~200 lines   (YAML loading)
lib/validator.py        ~300 lines   (validation)
lib/library.py          ~200 lines   (library lookups)
lib/db_battles.py       ~250 lines   (battle XML)
lib/db_encounters.py    ~300 lines   (story XML)
lib/db_npcs.py          ~350 lines   (NPC XML)
lib/db_items.py         ~150 lines   (item XML)
lib/db_parcels.py       ~100 lines   (parcel XML)
lib/db_images.py        ~150 lines   (image XML)
lib/xml_generator.py    ~200 lines   (db.xml assembly)
lib/packager.py         ~200 lines   (.mod creation)
lib/updater.py          ~300 lines   (update mode)
─────────────────────────────────────
Total:                  ~2850 lines
```

---

## Next Steps

Would you like me to:
1. **Build Phase 1-3** (core + validation) as a working foundation?
2. **Build Phase 4** (battle generation) to get first working output?
3. **Create starter templates** with TODO comments for you to fill in?
4. **Focus on update mode** specifically since that's your key requirement?

The full implementation is definitely doable but will take time to build properly and test!
