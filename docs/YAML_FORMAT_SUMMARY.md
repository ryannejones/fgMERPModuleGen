# Fantasy Grounds Module Generator - YAML Format Summary

## File Structure

```
my_adventure/
├── module.yaml         # REQUIRED - Module metadata
├── stories.yaml        # OPTIONAL - Narrative content
├── encounters.yaml     # OPTIONAL - Combat encounters
├── npcs.yaml          # OPTIONAL - Custom NPCs/creatures
├── items.yaml         # OPTIONAL - Custom items
├── parcels.yaml       # OPTIONAL - Treasure parcels
├── images.yaml        # OPTIONAL - Image references
└── images/            # OPTIONAL - Actual image files
    ├── map1.jpg
    └── portrait.png
```

## Quick Start

### Minimal Module
Just create `module.yaml`:
```yaml
name: mymodule
display_name: "My First Module"
author: "Your Name"
```

### Typical Module
Create these files:
- `module.yaml` - Metadata
- `stories.yaml` - Your adventure narrative
- `encounters.yaml` - Combat encounters
- `images.yaml` - Maps
- `images/` folder with map files

### Complex Module
All files for complete adventure with custom content.

## File Templates

All template files are provided:
- `template_module.yaml` - Module metadata
- `template_stories.yaml` - Story entries with examples
- `template_encounters.yaml` - Combat encounters
- `template_npcs.yaml` - Custom NPCs/creatures
- `template_items.yaml` - Custom items
- `template_parcels.yaml` - Treasure parcels
- `template_images.yaml` - Image references

## Key Concepts

### 1. Library Creatures vs Custom NPCs

**Use library creatures when possible:**
```yaml
# encounters.yaml
encounters:
  - name: "Orc Patrol"
    npcs:
      - creature: "Orc Scout"    # From library
        count: 3
```

**Create custom NPCs only when needed:**
```yaml
# npcs.yaml
npcs:
  - name: "Special Boss"
    level: 10
    hp: 120
    # ... full stats
```

### 2. References Between Files

**Stories can link to encounters:**
```yaml
# stories.yaml
stories:
  - name: "Day 1"
    sections:
      - type: link_encounter
        encounter_name: "Orc Patrol"  # Must match encounter name
```

**Encounters can use custom NPCs:**
```yaml
# encounters.yaml
encounters:
  - name: "Boss Fight"
    npcs:
      - creature: "Special Boss"  # Must match NPC name in npcs.yaml
```

**Items can be in parcels:**
```yaml
# parcels.yaml
parcels:
  - name: "Treasure Hoard"
    contents:
      - item: "Magic Sword +5"  # Must match item name in items.yaml
```

### 3. Auto-Detection

The script automatically:
- Detects which YAML files exist
- Assigns IDs to all entries
- Validates references between files
- Looks up library creatures
- Finds Arms Law weapons
- Links everything together

## Common Patterns

### Pattern 1: Simple Encounter
```yaml
# encounters.yaml
encounters:
  - name: "Random Orcs"
    exp: 200
    npcs:
      - creature: "Orc Scout"
        count: 2
        faction: foe
```

### Pattern 2: Story with Combat
```yaml
# stories.yaml
stories:
  - name: "Ambush!"
    sections:
      - type: read_aloud
        text: "Orcs leap from the trees!"
      - type: link_encounter
        encounter_name: "Random Orcs"
```

### Pattern 3: Loot from Encounter
```yaml
# parcels.yaml
parcels:
  - name: "Orc Loot"
    contents:
      - "20 gold pieces"
      - "Rusty weapons"

# stories.yaml (after encounter)
stories:
  - name: "After the Battle"
    sections:
      - type: gm_notes
        text: "Party finds loot on the bodies."
      - type: link_parcel
        parcel_name: "Orc Loot"
```

### Pattern 4: Map for Scene
```yaml
# images.yaml
images:
  - name: "Forest Clearing"
    file: "forest_clearing.jpg"

# stories.yaml
stories:
  - name: "The Clearing"
    sections:
      - type: read_aloud
        text: "You enter a clearing..."
      - type: link_image
        image_name: "Forest Clearing"
```

## Validation

The script validates:
- All referenced creatures exist (library or custom)
- All linked encounters/items/parcels exist
- All image files exist in images/ folder
- All weapons exist in Arms Law
- Required fields are present
- IDs are unique

## Error Handling

If validation fails, script shows:
- Which file has the error
- What's wrong (missing reference, invalid field, etc.)
- Suggestions for fixing

## Usage

```bash
# Generate module
python fg_module_generator.py my_adventure/

# Output
Creating module: My First Module
- Loaded module.yaml
- Loaded stories.yaml (3 entries)
- Loaded encounters.yaml (5 encounters)
- Loaded images.yaml (2 images)
- Validated all references
- Generated XML
- Created my_adventure.mod

Module ready: my_adventure.mod
```

## Next Steps

1. Copy template files to your adventure folder
2. Edit `module.yaml` with your module info
3. Add content to other YAML files as needed
4. Run the generator script
5. Load .mod file in Fantasy Grounds
6. Test!

