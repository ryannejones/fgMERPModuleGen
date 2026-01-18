# Fantasy Grounds MERP Module - YAML Schemas

This document defines the authoritative schemas for all YAML files used in the Fantasy Grounds MERP module generator.

---

## module.yaml

### Description
Module metadata and configuration. Generate this file LAST after all other YAML files are complete.

### Schema
```yaml
name: "module_identifier"                    # REQUIRED: lowercase, underscores only
display_name: "Human Readable Module Name"   # REQUIRED: displayed in Fantasy Grounds
author: "Author Name"                        # REQUIRED: your name or organization
category: "Middle-earth Role Playing"        # REQUIRED: must be exactly this
ruleset: "RolemasterClassic"                 # REQUIRED: must be exactly this

include:                                     # REQUIRED: feature flags
  stories: true                              # Include stories tab
  encounters: true                           # Include encounters/battles tab
  npcs: true                                 # Include NPCs tab
  items: true                                # Include items tab
  parcels: true                              # Include treasure parcels
  images: true                               # Include images

options:                                     # REQUIRED: generation options
  validate: true                             # Run validation checks
  auto_id: true                              # Auto-assign IDs
  overwrite: false                           # Overwrite existing output files

output:                                      # REQUIRED: output configuration
  filename: "modulename.mod"                 # Output .mod filename
  directory: "./output"                      # CRITICAL: Must be "./output" (relative path, NOT absolute path like /mnt/user-data/outputs)
```

---

## items.yaml

### Description
Define all items (weapons, armor, magic items, herbs, treasures). Items MUST be defined here before being referenced in npcs.yaml or parcels.yaml.

### Schema
```yaml
items:
  # Library item (no modifications)
  - name: "Broadsword"
  
  # Library item with modifications
  - name: "Gihellin's Dagger"
    based_on: "Dagger"
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "Item description text"
      notes:
        "@type": "formattedtext"
        "_text": "Special properties or notes"
  
  # Custom item (not in library)
  - name: "Custom Item"
    based_on: ""
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "Complete item description"
```

### Field Definitions
- **name** (REQUIRED): Item name, can include bonuses (e.g., "Broadsword +10")
- **based_on** (OPTIONAL): Library item name from Arms Law; use `""` for custom items
- **modifications** (OPTIONAL): Dictionary of fields to override
  - **description**: Full item description (use @type and _text structure)
  - **notes**: Additional notes about mechanics or properties
  - Other fields can be added as needed

### Critical Rules
- All items referenced anywhere else MUST exist here first
- Coins do NOT go in items.yaml (they go in parcels.yaml)
- Use `@type: "formattedtext"` and `_text:` for all text fields

---

## npcs.yaml

### Description
Define custom NPCs based on library creatures/templates. NPCs can be referenced in encounters.yaml and stories.yaml.

**CRITICAL:** Every creature used in encounters.yaml MUST have an entry in npcs.yaml, even if it's just a minimal library reference.

### Schema
```yaml
npcs:
  - name: "NPC Name"                         # REQUIRED: unique identifier
    based_on: "Library Creature Name"        # REQUIRED: from Character Law
    level: 10                                # OPTIONAL: character level
    hp: 75                                   # OPTIONAL: hit points override
    at: 15                                   # OPTIONAL: armor type (RM number)
    db: 50                                   # OPTIONAL: defensive bonus
    baserate: 50                             # OPTIONAL: movement rate
    race: "Human"                            # OPTIONAL: character race
    group: "NPCs"                            # OPTIONAL: "NPCs" or "Monsters"
    weapons:                                 # OPTIONAL: weapon list
      - weapon: "Broadsword"                 # Must exist in items.yaml
        ob: 110
      - weapon: "Long Bow"
        ob: 75
    defences:                                # OPTIONAL: defensive items
      - name: "Shield"
        melee_bonus: 25
        missile_bonus: 25
    abilities: "Text description"            # OPTIONAL: special abilities
    spells: "Spell list text"                # OPTIONAL: spells known
    stats: "Co86, Ag81..."                   # OPTIONAL: full stat line
    description: "Physical and personality"  # OPTIONAL: NPC description
```

### Field Definitions
- **name** (REQUIRED): NPC's name
- **based_on** (REQUIRED): Base creature from library (e.g., "Fighter", "Orc, Lesser", "Pure Essence Spell User")
- **level** (OPTIONAL): Character level
- **hp** (OPTIONAL): Hit points (overrides library default)
- **at** (OPTIONAL): Armor type as RM number
- **db** (OPTIONAL): Total defensive bonus
- **baserate** (OPTIONAL): Movement rate (usually 50 or 60)
- **race** (OPTIONAL): Character's race
- **group** (OPTIONAL): "NPCs" for humanoids, "Monsters" for creatures
- **weapons** (OPTIONAL): List of weapons with offensive bonuses
- **defences** (OPTIONAL): Shields, armor with bonuses
- **abilities** (OPTIONAL): Special abilities (simple string - library converts to formattedtext)
- **spells** (OPTIONAL): Spell lists and levels
- **stats** (OPTIONAL): Full stat line if needed
- **description** (OPTIONAL): Physical and personality (simple string - library converts to formattedtext)

### Common Library Creatures
- "Pure Essence Spell User" (wizards)
- "Pure Channeling Spell User" (clerics)
- "Fighter", "Ranger", "Rogue"
- "Orc, Lesser", "Orc, Greater", "Orc (leader)"
- "Giant Spider", "Warg", "Stone Troll"

---

## encounters.yaml

### Description
Define combat encounters. Can reference NPCs from npcs.yaml or library creatures directly.

### Schema
```yaml
encounters:
  - name: "Encounter Name"                   # REQUIRED: unique identifier
    exp: 400                                 # OPTIONAL: experience points
    npcs:                                    # REQUIRED: list of NPCs/creatures
      # Reference custom NPC from npcs.yaml
      - name: "Custom NPC Name"
        count: 1
        faction: "foe"
        display_name: "Display Name"         # OPTIONAL: override name
      
      # Reference library creature (must also exist in npcs.yaml)
      - name: "Orc, Lesser"
        count: 5
        faction: "foe"
```

### Field Definitions
- **name** (REQUIRED): Encounter identifier
- **exp** (OPTIONAL): Experience point award
- **npcs** (REQUIRED): List of NPCs in encounter
  - **name** (REQUIRED): NPC name (must exist in npcs.yaml)
  - **count** (REQUIRED): Number of this NPC type
  - **faction** (REQUIRED): Must be "foe", "friend", or "neutral"
  - **display_name** (OPTIONAL): Override name shown in Fantasy Grounds

### Critical Rules
- Faction must be exactly "foe", "friend", or "neutral" (case-sensitive)
- All NPCs must exist in npcs.yaml first (even library creatures need minimal entries)

---

## parcels.yaml

### Description
Define treasure parcels containing coins and items. Items must exist in items.yaml first.

### Schema
```yaml
parcels:
  - name: "Parcel Name"                      # REQUIRED: unique identifier
    description: "Context description"       # OPTIONAL: when/where found
    coins:                                   # OPTIONAL: coin amounts
      MP: 0                                  # Mithril Pieces
      PP: 0                                  # Platinum Pieces
      GP: 50                                 # Gold Pieces
      SP: 120                                # Silver Pieces
      BP: 0                                  # Bronze Pieces
      CP: 0                                  # Copper Pieces
      TP: 0                                  # Tin Pieces
      IP: 0                                  # Iron Pieces
    items:                                   # OPTIONAL: item list
      - name: "Item Name"                    # Must exist in items.yaml
        count: 1
```

### Field Definitions
- **name** (REQUIRED): Parcel identifier
- **description** (OPTIONAL): Context about the treasure
- **coins** (OPTIONAL): Dictionary of coin types and amounts
  - Only include coin types with non-zero amounts
- **items** (OPTIONAL): List of items with counts
  - **name** (REQUIRED): Item name (must exist in items.yaml)
  - **count** (OPTIONAL): Number of items (defaults to 1)

### Coin Types
- **MP**: Mithril Pieces (most valuable)
- **PP**: Platinum Pieces
- **GP**: Gold Pieces
- **SP**: Silver Pieces
- **BP**: Bronze Pieces
- **CP**: Copper Pieces
- **TP**: Tin Pieces
- **IP**: Iron Pieces (least valuable)

---

## stories.yaml

### Description
Define narrative content with text sections and links to other entities. Stories organize the adventure content.

### Schema
```yaml
stories:
  - name: "Story Name"                       # REQUIRED: unique identifier
    sections:                                # REQUIRED: at least one section
      # Text sections
      - type: "header"
        text: "Section Title"
      
      - type: "read_aloud"
        text: "Text to read to players"
      
      - type: "gm_notes"
        text: "GM-only information"
      
      # Link sections
      - type: "link_encounter"
        encounter_name: "Encounter Name"
        link_text: "Optional display text"   # OPTIONAL
      
      - type: "link_npc"
        npc_name: "NPC Name"
        link_text: "Optional display text"   # OPTIONAL
      
      - type: "link_item"
        item_name: "Item Name"
        link_text: "Optional display text"   # OPTIONAL
      
      - type: "link_parcel"
        parcel_name: "Parcel Name"
        link_text: "Optional display text"   # OPTIONAL
      
      - type: "link_image"
        image_name: "Image Name"
        link_text: "Optional display text"   # OPTIONAL
```

### Field Definitions
- **name** (REQUIRED): Story identifier
- **sections** (REQUIRED): List of sections (minimum 1)
  - **type** (REQUIRED): Section type (see below)
  - **text** (CONDITIONAL): Required for header/read_aloud/gm_notes
  - **{entity}_name** (CONDITIONAL): Required for link types
  - **link_text** (OPTIONAL): Custom display text for links

### Section Types
**Text Types:**
- **header**: Section titles
- **read_aloud**: Text for players
- **gm_notes**: GM-only information

**Link Types:**
- **link_encounter**: Link to encounter (requires encounter_name)
- **link_npc**: Link to NPC (requires npc_name)
- **link_item**: Link to item (requires item_name)
- **link_parcel**: Link to parcel (requires parcel_name)
- **link_image**: Link to image/map (requires image_name)

### Text Formatting
For multiline text, use YAML multiline syntax:
```yaml
- type: gm_notes
  text: |
    First paragraph of notes.
    
    Second paragraph with more details.
```

---

## images.yaml (OPTIONAL)

### Description
If not provided, images are auto-detected from the images/ folder. Use this file to specify custom image metadata.

### Schema
```yaml
images:
  - name: "Image Display Name"               # REQUIRED: display name
    file: "filename.png"                     # REQUIRED: filename in images/ folder
```

### Auto-Detection
If images.yaml is not provided, the generator will:
1. Scan the images/ folder
2. Use filename (without extension) as display name
3. Include all common image formats (.png, .jpg, .jpeg, .webp, .gif)

---

## Generation Order (MANDATORY)

Files must be generated in this order:

1. **items.yaml** - Must be first (NPCs and parcels reference items)
2. **npcs.yaml**
3. **encounters.yaml**
4. **parcels.yaml**
5. **images/** - Extract and place images BEFORE stories (stories link to images)
6. **stories.yaml** - Must come after images
7. **module.yaml** - Must be LAST

---

## Validation Rules

### Cross-References
All references must resolve:
- Items in npcs.yaml weapons → must exist in items.yaml
- Items in parcels.yaml → must exist in items.yaml
- NPCs in encounters.yaml → must exist in npcs.yaml OR be library creatures
- Encounters in stories.yaml links → must exist in encounters.yaml
- NPCs in stories.yaml links → must exist in npcs.yaml OR be library creatures
- Items in stories.yaml links → must exist in items.yaml
- Parcels in stories.yaml links → must exist in parcels.yaml

### Required Fields
- All REQUIRED fields must be present
- Field types must match schema
- Faction in encounters must be "foe", "friend", or "neutral"

### Naming Rules
- Module name: lowercase, underscores only
- All other names: human-readable, proper capitalization
- Image files: snake_case derived from entity names

---

## Common Patterns

### Pattern 1: Simple Library Item
```yaml
items:
  - name: "Broadsword"
```

### Pattern 2: Custom Magical Item
```yaml
items:
  - name: "Flaming Sword +10"
    based_on: "Broadsword"
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "A broadsword wreathed in magical flames."
```

### Pattern 3: Custom NPC
```yaml
npcs:
  - name: "Captain of the Guard"
    based_on: "Fighter"
    level: 5
    hp: 70
    at: 15
    db: 40
    weapons:
      - weapon: "Broadsword"
        ob: 85
```

### Pattern 4: Encounter with Mixed NPCs
```yaml
encounters:
  - name: "Guard Post"
    npcs:
      - name: "Captain of the Guard"  # Custom NPC
        count: 1
        faction: "foe"
      - name: "Fighter"               # Library creature
        level: 3
        count: 4
        faction: "foe"
        display_name: "Guard"
```

### Pattern 5: Story with Links
```yaml
stories:
  - name: "The Ambush"
    sections:
      - type: header
        text: "An Unexpected Attack"
      - type: read_aloud
        text: "Arrows whistle from the trees!"
      - type: link_encounter
        encounter_name: "Guard Post"
```

---

*This schema is authoritative and matches the fgMERPModuleGen generator requirements.*
