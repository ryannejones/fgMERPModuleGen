# When Do I Need Custom Content?

## Quick Decision Guide

### Do I need npcs.yaml?

**NO - Use the library** if your NPCs are:
-  Orc Scout, Orc Uruk, Orc Bulkupar
-  Wolf, Wolf - Alpha, Warg
-  Giant Spider, Troll
-  Ranger Level 1, 3, or 5
-  Fighter Level 3 or 5
-  Animist Level 3 or 5

**YES - Create custom** if you need:
-  Different profession (Thief, Monk, Bard, etc.)
-  Different level than available (Ranger Level 7, Fighter Level 10)
-  Unique boss NPC (Skauril the Necromancer)
-  Special abilities not in library
-  Creatures not listed above (Balrog, Dragon, Wraith, etc.)

**Example - NO custom NPC needed:**
```yaml
# encounters.yaml
encounters:
  - name: "Forest Patrol"
    npcs:
      - creature: "Ranger Level 3"  # Already in library!
        count: 2
```

**Example - YES custom NPC needed:**
```yaml
# npcs.yaml - Must create because Thief Level 5 isn't in library
npcs:
  - name: "Thief Level 5"
    level: 5
    hp: 40
    at: 10
    # ... full stats

# encounters.yaml
encounters:
  - name: "Thieves Guild"
    npcs:
      - creature: "Thief Level 5"
        count: 3
```

---

### Do I need items.yaml?

**NO - Use references** if your items are:
-  Standard weapons (Scimitar, Long Bow, Dagger, etc.) - 75 weapons in Arms Law
-  Mundane equipment (Rope, Backpack, Torch, etc.) - 73 items in Character Law
-  Common herbs - 100 herbs in Character Law
-  Food/lodging - 18 items in Character Law
-  Transport (Horses, carts, etc.) - 33 items in Character Law

**YES - Create custom** if you need:
-  Magical weapons (+5 sword, flaming dagger)
-  Magical armor (+10 chain mail, mithril plate)
-  Magic items (ring of invisibility, staff of power)
-  Potions (healing, strength, flight)
-  Unique quest items (ancient crown, royal seal)
-  Cursed items

**Example - NO custom item needed:**
```yaml
# parcels.yaml
parcels:
  - name: "Orc Loot"
    contents:
      - "20 gold pieces"
      - "Scimitar"           # Standard weapon, no definition needed
      - "50 feet of rope"    # Standard equipment
      - "5 days rations"     # Standard food
```

**Example - YES custom item needed:**
```yaml
# items.yaml - Must create because it's magical
items:
  - name: "Flaming Sword +10"
    type: "Weapon"
    description: "A sword wreathed in flames"
    properties:
      weapon_bonus: 10
      base_weapon: "Broadsword"
      special: "1-6 fire damage"

# parcels.yaml
parcels:
  - name: "Dragon Hoard"
    contents:
      - "1000 gold pieces"
      - item: "Flaming Sword +10"  # Reference to custom item
```

---

## How to Check What's Available

### 1. Check the Creature Library
Look in `creature_npc_library.json`:
```json
{
  "creatures": {
    "Orc Scout": {...},
    "Warg": {...},
    etc.
  },
  "npcs": {
    "Ranger Level 3": {...},
    etc.
  }
}
```

If your creature is there → No custom NPC needed  
If not → Create in npcs.yaml

### 2. Check Arms Law Weapons
Look in `arms_law_weapons.json`:
```json
{
  "weapons": [
    {"id": "00022", "name": "Scimitar", "table": "ALT-22"},
    {"id": "00015", "name": "Long Bow", "table": "AMT-07"},
    etc.
  ]
}
```

If your weapon is there → No custom item needed (unless it's magical)  
If not OR if magical → Create in items.yaml

### 3. Check Character Law Equipment
Look in these files:
- `character_law_accessories.json` - Rope, backpack, torches, etc.
- `character_law_herbs.json` - Healing herbs
- `character_law_food.json` - Food, ale, lodging
- `character_law_transport.json` - Horses, carts, saddles

If your item is there → Just use the name in parcels  
If not OR if magical → Create in items.yaml

---

## Common Scenarios

### Scenario 1: "I need orcs for my adventure"
**Answer:** Use the library
```yaml
# encounters.yaml
- creature: "Orc Scout"      # Level 6, already defined
- creature: "Orc Uruk"       # Level 8, already defined
- creature: "Orc - Bulkupar" # Level 10 commander, already defined
```

### Scenario 2: "I need a Level 7 Ranger"
**Answer:** Create custom NPC (Level 7 not in library)
```yaml
# npcs.yaml
- name: "Ranger Level 7"
  level: 7
  hp: 55
  at: 10
  # ... etc
```

### Scenario 3: "I need a magic sword"
**Answer:** Create custom item (magic items not in references)
```yaml
# items.yaml
- name: "Elven Blade +5"
  type: "Weapon"
  # ... etc
```

### Scenario 4: "I need rope and torches"
**Answer:** Use standard items (in Character Law)
```yaml
# parcels.yaml
contents:
  - "50 feet of rope"      # No definition needed
  - "10 torches"           # No definition needed
```

### Scenario 5: "I need a unique boss villain"
**Answer:** Create custom NPC (unique character)
```yaml
# npcs.yaml
- name: "Lord Darkness"
  level: 15
  # ... full custom stats
```

### Scenario 6: "I need wolves for a random encounter"
**Answer:** Use the library
```yaml
# encounters.yaml
- creature: "Wolf"           # Level 3, already defined
- creature: "Wolf - Alpha"   # Level 5, already defined
```

### Scenario 7: "I need a Thief"
**Answer:** Create custom NPC (Thief not in library)
```yaml
# npcs.yaml
- name: "Thief Level 5"
  profession: "Thief"
  # ... stats based on Character Law or your book
```

---

## Quick Reference: What's in the Library

### Creatures (8 total):
1. Orc Scout (Level 6)
2. Orc Uruk (Level 8)
3. Orc - Bulkupar (Level 10)
4. Wolf (Level 3)
5. Wolf - Alpha (Level 5)
6. Warg (Level 5)
7. Giant Spider (Level 4)
8. Troll (Level 8)

### NPCs (7 total):
1. Ranger Level 1
2. Ranger Level 3
3. Ranger Level 5
4. Fighter Level 3
5. Fighter Level 5
6. Animist Level 3
7. Animist Level 5

### Standard Weapons (75 total):
Scimitar, Broadsword, Short Sword, Long Sword, Dagger, Staff, Mace, Battle Axe, War Hammer, Spear, Long Bow, Short Bow, Crossbows, and 60+ more

### Standard Equipment (200+ items):
Rope, Backpack, Torches, Bedroll, Waterskin, Rations, Horses, Carts, 100 herbs, etc.

---

## Rule of Thumb

**If it's mundane and common** → It's probably in the references  
**If it's magical or unique** → You need to create it  
**If it's a standard creature/NPC** → Check the library first  
**If it's a boss/villain/special** → You'll need to create it

When in doubt:
1. Check the library/reference files
2. If not there → Create custom
3. Still unsure → Create custom (better safe than sorry)

---

## Pro Tips

### Tip 1: You can always add to the library
If you find yourself creating the same NPCs repeatedly, add them to `creature_npc_library.json` permanently.

### Tip 2: Start simple
First adventure: Use only library creatures and standard items  
Later adventures: Add custom content as needed

### Tip 3: Mix and match
```yaml
# Perfectly fine to mix library and custom
encounters:
  - name: "Mixed Group"
    npcs:
      - creature: "Orc Scout"        # From library
        count: 3
      - creature: "Evil Wizard"      # Custom from npcs.yaml
        count: 1
```

### Tip 4: Magic = Custom
If the word "magic" or "+X" appears in the item name → Create in items.yaml  
If it's mundane → Just use the name

### Tip 5: When converting published adventures
Most published MERP/Rolemaster adventures will need:
-  Custom NPCs (for unique villains and special encounters)
-  Custom items (for quest items and treasure)
-  Stories (for narrative)
-  Encounters (for battles)
-  Mix of library creatures (for common enemies) and custom (for unique ones)
