# Spell References System

## Overview

The Spell Law module contains **162 spell lists** (54 per realm) but **no individual spell definitions**. This is by design - GMs assign spell lists to NPCs and populate them with spells in Fantasy Grounds.

## Spell List Structure

### Three Realms
1. **Channeling** - 54 spell lists (Clerics, Animists, etc.)
2. **Essence** - 54 spell lists (Mages, Illusionists, etc.)
3. **Mentalism** - 54 spell lists (Mystics, Healers, etc.)

### Sample Spell Lists

**Channeling:**
- Barrier Law
- Concussion's Way
- Detection Mastery
- Light's Way
- Lofty Movements

**Essence:**
- Delving Ways
- Detecting Ways
- Elemental Shields
- Essence Hand
- Essence's Perceptions

**Mentalism:**
- Anticipations
- Attack Avoidance
- Brilliance
- Cloaking
- Damage Resistance

## How Spells Work in NPCs

### NPCs Have Empty Spell Sections

When you extract an NPC from Character Law:
```json
{
  "spells": {}  // Empty - GM populates in Fantasy Grounds
}
```

This is correct! NPCs come with empty spell sections ready for GMs to add spell lists.

### Adding Spell Lists in YAML (Optional)

Users CAN specify spell lists in YAML if they want to pre-populate:

```yaml
npcs:
  - name: "Evil Cleric"
    based_on: "Cleric"
    level: 10
    spell_lists:
      - name: "Barrier Law"
        realm: "channeling"
      - name: "Concussion's Way"
        realm: "channeling"
```

This would add references to those spell lists in the generated NPC.

### Or Add in Fantasy Grounds (Typical)

Most GMs prefer to add spells in Fantasy Grounds:
1. Open the NPC in Fantasy Grounds
2. Click on Spells section
3. Drag spell lists from Spell Law module
4. Fantasy Grounds creates the references automatically

## Spell List Reference Format

Each spell list has a reference path:
```
reference.spelllist.{realm}.lists.{list-id}@Spell Law
```

Example:
```
reference.spelllist.channeling.lists.list-001@Spell Law
```

This points to "Barrier Law" in the Channeling realm.

## Module Generation

### Option 1: Empty Spell Section (Default)
```xml
<npc>
  <id-00001>
    <name type="string">Evil Cleric</name>
    <spells>
      <!-- Empty - GM adds in Fantasy Grounds -->
    </spells>
  </id-00001>
</npc>
```

### Option 2: Pre-populate Spell Lists (If User Specifies)
```xml
<npc>
  <id-00001>
    <name type="string">Evil Cleric</name>
    <spells>
      <id-00001>
        <name type="string">Barrier Law</name>
        <open type="windowreference">
          <class>spelllist</class>
          <recordname>reference.spelllist.channeling.lists.list-001@Spell Law</recordname>
        </open>
      </id-00001>
      <id-00002>
        <name type="string">Concussion's Way</name>
        <open type="windowreference">
          <class>spelllist</class>
          <recordname>reference.spelllist.channeling.lists.list-002@Spell Law</recordname>
        </open>
      </id-00002>
    </spells>
  </id-00001>
</npc>
```

## Spell Reference Table

`spell_references.json` contains 162 spell lists organized by realm:

```json
{
  "spell_lists": {
    "barrier law": {
      "name": "Barrier Law",
      "id": "list-001",
      "realm": "channeling",
      "reference_path": "reference.spelllist.channeling.lists.list-001@Spell Law"
    }
  },
  "realms": {
    "channeling": [ /* 54 spell lists */ ],
    "essence": [ /* 54 spell lists */ ],
    "mentalism": [ /* 54 spell lists */ ]
  }
}
```

## YAML Examples

### Minimal (No Spells)
```yaml
npcs:
  - name: "Animist Scout"
    based_on: "Animist"
    level: 7
    # No spells specified - GM adds in FG
```

### With Spell Lists
```yaml
npcs:
  - name: "Animist Scout"
    based_on: "Animist"
    level: 7
    spell_lists:
      - "Barrier Law"        # System finds in channeling realm
      - "Detection Mastery"  # Based on Animist = Channeling
```

### Specify Realm Explicitly (If Ambiguous)
```yaml
npcs:
  - name: "Hybrid Caster"
    based_on: "Hybrid Spell User"
    level: 10
    spell_lists:
      - name: "Barrier Law"
        realm: "channeling"
      - name: "Delving Ways"
        realm: "essence"
```

## Matching Spell Lists

The entity matcher can find spell lists by name:

```python
# Find a spell list
result = matcher.match_spell_list("Barrier Law")
# Returns reference path and realm info
```

Uses same matching as NPCs/items:
1. Exact match (case-insensitive)
2. Fuzzy match if needed
3. Suggests alternatives if not found

## Why Individual Spells Aren't Included

1. **Spell Law module doesn't contain them** - Only list names
2. **GMs customize** - Different campaigns have different spells
3. **Flexible system** - GMs choose which spells NPCs know
4. **Module would be huge** - Adding every spell would bloat it

## Summary

✅ **162 spell lists extracted** (54 per realm)
✅ **Reference table created** (`spell_references.json`)
✅ **NPCs have empty spell sections** (by design)
✅ **Users can optionally pre-populate** in YAML
✅ **GMs typically add spells** in Fantasy Grounds

**Recommended approach:**
- Leave spell sections empty in generated modules
- Let GMs add spell lists in Fantasy Grounds
- Provide spell list reference table for documentation
- Support optional YAML specification for power users

The system is complete and flexible!
