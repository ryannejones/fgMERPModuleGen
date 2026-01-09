# YAML Format Guide

## Overview

The YAML format leverages the complete library of 715 NPCs/creatures and 1,257 items extracted from ICE rulebooks.

## Key Principles

1. **Reference library entries when possible** - Let the generator pull complete data
2. **Use `based_on` for variants** - Create custom NPCs/items from templates
3. **Be explicit about choices** - Don't rely on fuzzy matching
4. **Items defined once** - NPCs reference module items

## NPCs Format

### Simple Reference (Exact Match)
```yaml
npcs:
  - name: "Wolf"  # Exact match in library
  
  - name: "Ranger"
    level: 5  # Profession-based, specify level
```

### Custom NPC (Based On Template)
```yaml
npcs:
  - name: "Skauril the Conjurer"
    based_on: "Pure Channeling Spell User"  # Template from library
    level: 15
    modifications:
      hits:
        "@type": "number"
        "_text": "130"
      armortype:
        "@type": "number"
        "_text": "15"
      defensivebonus:
        "@type": "number"
        "_text": "30"
    description: "Custom description here"
```

### Important Notes

**Profession Mappings:**
- "Animist" → "Pure Channeling Spell User"
- "Scout" → "Ranger"
- "Warrior" → "Fighter"

**Creature Names - Be Specific:**
- ❌ "Orc Scout" (doesn't exist)
- ✅ "Orc, Lesser" (exists - use for scouts)
- ✅ "Orc (leader)" (exists - use for uruks/elites)
- ✅ "Orc (commander)" (exists - use for commanders)

**Available Orc Types:**
- `Orc (non-combatant)` - Civilians, workers
- `Orc, Lesser` - Regular warriors, scouts
- `Orc (leader)` - Uruks, elite warriors
- `Orc (commander)` - Leaders, commanders
- `Orc, Greater` - Powerful variants

## Items Format

### Simple Reference (From Library)
```yaml
items:
  - name: "Broadsword"  # Exact match, pulls complete data
  
  - name: "Long Bow"
    count: 5  # Optional count override
```

### Custom Item (Based On Template)
```yaml
items:
  - name: "Gihellin's Dagger"
    based_on: "Dagger"
    modifications:
      bonus:
        "@type": "number"
        "_text": "5"
      description:
        "@type": "formattedtext"
        "_text": "Enchanted blade that glows blue near darkness"
```

### Common Items to Include
```yaml
items:
  # Include items that NPCs will use
  - name: "Broadsword"
  - name: "Scimitar"
  - name: "Long Bow"
  - name: "Dagger"
  
  # Custom magical items
  - name: "Magic Sword +5"
    based_on: "Broadsword"
    modifications:
      bonus:
        "@type": "number"
        "_text": "5"
```

## Encounters Format

### Using Library NPCs
```yaml
encounters:
  - name: "Bridge Encounter"
    exp: 800
    npcs:
      - name: "Ranger"
        level: 5
        count: 1
        faction: foe
        display_name: "Bridge Ranger"
      
      - name: "Fighter"
        level: 3
        count: 4
        faction: foe
```

### Using Custom NPCs (from npcs.yaml)
```yaml
encounters:
  - name: "Boss Fight"
    npcs:
      - name: "Skauril the Conjurer"  # Defined in npcs.yaml
        count: 1
        faction: foe
```

### Using Based-On in Encounters
```yaml
encounters:
  - name: "Orc Patrol"
    npcs:
      - name: "Orc Scout"
        based_on: "Orc, Lesser"  # Create variant in encounter
        count: 10
        faction: foe
      
      - name: "Uruk Leader"
        based_on: "Orc (leader)"
        count: 1
        faction: foe
```

## Parcels Format

### With Item References
```yaml
parcels:
  - name: "Treasure Chest"
    description: "Loot from defeated enemies"
    coins:
      GP: 50
      SP: 100
    items:
      - name: "Broadsword"  # References item from items.yaml
        count: 3
      - name: "Magic Sword +5"  # Custom item from items.yaml
        count: 1
```

### Important: Items Must Exist
- All items in parcels must be defined in `items.yaml`
- Generator creates references to module items
- When distributed, FG copies complete item data to character

## Modifications Format

When using `modifications`, follow the XML structure from library:

### Simple Number Field
```yaml
modifications:
  hits:
    "@type": "number"
    "_text": "100"
```

### Simple String Field
```yaml
modifications:
  name:
    "@type": "string"
    "_text": "Custom Name"
```

### Formatted Text
```yaml
modifications:
  description:
    "@type": "formattedtext"
    "_text": "Multi-line description here"
```

### Complex Nested Structure
```yaml
modifications:
  attacktable:
    tableid:
      "@type": "string"
      "_text": "ALT-05"
```

## Common Patterns

### Pattern 1: Standard Encounter
```yaml
encounters:
  - name: "Bandit Ambush"
    npcs:
      - name: "Rogue"
        level: 3
        count: 5
        faction: foe
```

### Pattern 2: Mixed Encounter (Library + Custom)
```yaml
encounters:
  - name: "Boss + Minions"
    npcs:
      - name: "Evil Wizard"  # Custom from npcs.yaml
        count: 1
        faction: foe
      
      - name: "Orc, Lesser"  # Library creature
        count: 8
        faction: foe
```

### Pattern 3: Named Custom Variants
```yaml
npcs:
  - name: "Orc Scout Leader"
    based_on: "Orc, Lesser"
    modifications:
      hits:
        "@type": "number"
        "_text": "75"

encounters:
  - name: "Scout Patrol"
    npcs:
      - name: "Orc Scout Leader"  # Use custom NPC
        count: 1
      - name: "Orc, Lesser"  # Regular scouts
        count: 6
```

## Migration from Old Format

### Old Format (v10_FINAL)
```yaml
npcs:
  - name: "Guard"
    level: 5
    hp: 50
    at: 12
    weapons:
      - weapon: "Long Sword"
        ob: 65
```

### New Format (v0.11)
```yaml
npcs:
  - name: "Guard"
    based_on: "Fighter"
    level: 5
    modifications:
      hits:
        "@type": "number"
        "_text": "50"
      armortype:
        "@type": "number"
        "_text": "12"
```

### Why Change?

**Old format:**
- Created NPCs from scratch
- Limited data
- No connection to library

**New format:**
- Leverages complete library (715 NPCs)
- Full stat blocks automatically
- Skills, spells, equipment all included
- Single point of truth

## Troubleshooting

### "NPC not found"
- Check exact spelling
- Use profession mappings (Animist → Pure Channeling Spell User)
- For creatures, be specific (Orc Scout → Orc, Lesser)
- Check available names: see library documentation

### "Item not found"
- Check exact spelling
- Common items: Broadsword, Scimitar, Long Bow, Dagger
- Add item to items.yaml first if custom

### "Modifications not working"
- Use correct XML structure with @type and _text
- Check library data for field names
- Simple fields: hits, armortype, defensivebonus
- Complex fields: use nested structure

## Best Practices

1. **Define common items once in items.yaml**
   ```yaml
   items:
     - name: "Broadsword"
     - name: "Scimitar"
     - name: "Long Bow"
   ```

2. **Use library NPCs when possible**
   ```yaml
   npcs:
     - name: "Wolf"  # Not: based_on Wolf
   ```

3. **Be explicit about creature types**
   ```yaml
   # Good
   - name: "Orc Scout"
     based_on: "Orc, Lesser"
   
   # Bad (ambiguous)
   - name: "Orc Scout"
   ```

4. **Group related custom NPCs in npcs.yaml**
   ```yaml
   npcs:
     - name: "Boss"
       based_on: "Fighter"
       level: 15
     
     - name: "Boss Lieutenant"
       based_on: "Fighter"
       level: 10
   ```

5. **Items in parcels must exist in items.yaml**
   ```yaml
   # items.yaml
   items:
     - name: "Magic Ring"
       based_on: "Ring"
   
   # parcels.yaml
   parcels:
     - name: "Treasure"
       items:
         - name: "Magic Ring"  # Must match exactly
   ```

## Example: Complete Module

See `examples/test_chapter6_updated/` for a complete working example using the new format.

**Files:**
- `module.yaml` - Module metadata
- `npcs.yaml` - 4 custom NPCs using based_on
- `items.yaml` - 5 custom items + 7 standard items
- `encounters.yaml` - 6 encounters mixing library + custom NPCs
- `parcels.yaml` - 6 treasure parcels referencing items
- `stories.yaml` - Story entries (unchanged)

## Summary

✅ **Reference library entries** - Simple and complete
✅ **Use based_on for variants** - Flexible customization  
✅ **Be explicit** - No ambiguity
✅ **Items defined once** - Single point of truth
✅ **Complete stat blocks** - All data from library

The new format is more verbose but provides complete, accurate data from the official rulebooks.
