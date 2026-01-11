# Fantasy Grounds Module Templates

## Files Included

### Empty Templates (for scripting)
- `template_definition.xml` - Module metadata template
- `template_db.xml` - Complete empty db.xml with all sections and examples

### Minimal Working Example
- `minimal_example_definition.xml` - Working definition.xml
- `minimal_example_db.xml` - Minimal working db.xml with one of each content type

## How to Create a Module Manually

1. Copy `template_definition.xml` and `template_db.xml`
2. Replace placeholders:
   - `MODULE_INTERNAL_NAME` - lowercase, no spaces (e.g., "skaurilsarmy")
   - `MODULE_DISPLAY_NAME` - Display name (e.g., "Skauril's Army")
   - `AUTHOR_NAME` - Your name
3. Add your content to the sections in db.xml
4. Zip both files together (not in a folder)
5. Rename .zip to .mod
6. Load in Fantasy Grounds

## Module Structure

### definition.xml
Contains module metadata:
- Internal name (used in XML references)
- Display name (shown in FG)
- Author name
- Ruleset (RolemasterClassic)

### db.xml Sections

**battle** - Combat Encounters (appears in "Encounters" tab)
- Groups of NPCs for combat
- Links to NPC definitions
- Can reference NPCs from other modules (like Character Law)

**encounter** - Story Entries (appears in "Stories" tab)  
- Narrative text and read-aloud content
- Uses formattedtext with <h>, <p>, <frame> tags
- Can link to battles, NPCs, items, images

**npc** - NPCs
- Custom NPCs with full stats
- Or just empty if only referencing other modules

**item** - Items and Treasure
- Individual items, magic items, mundane gear

**treasureparcels** - Grouped Treasure (optional)
- Collections of items to distribute

**tables** - Random Tables (optional)
- Rollable encounter tables, random events

**library** - Organization
- Makes content appear in Library tab
- Must match MODULE_INTERNAL_NAME

## Content Formatting

### Read-Aloud Text (for players)
```xml
<frame>You see a dark cave ahead...</frame>
```

### GM Notes
```xml
<p>The orcs will ambush if the party enters.</p>
```

### Section Headers
```xml
<h>Day 1</h>
```

### Links to Other Content
```xml
<linklist>
    <link class="battle" recordname="battle.id-00001">Encounter: Orc Ambush</link>
    <link class="npc" recordname="npc.id-00026@Character Law">Ranger Level 5</link>
</linklist>
```

## Referencing Core Modules

### NPCs from Character Law
```xml
<recordname>npc.id-00026@Character Law</recordname>  <!-- Ranger Level 5 -->
```

### Weapons from Arms Law
```xml
<recordname>weaponlist.standardweapons.id-00022@Arms Law</recordname>  <!-- Scimitar -->
```

### Items from Character Law
```xml
<recordname>equipment.accessories.id-00051@Character Law</recordname>  <!-- Rope -->
```

See the reference JSON files for complete lists of available IDs.

## Testing Your Module

1. Place .mod file in Fantasy Grounds modules folder:
   - Windows: `C:\Users\[YourName]\AppData\Roaming\SmiteWorks\Fantasy Grounds\modules\`
2. Launch Fantasy Grounds
3. Load your campaign
4. Go to Library → Modules
5. Load your module
6. Check that content appears in Encounters, Stories, NPCs, Items tabs

## Troubleshooting

**Module doesn't load**
- Check XML syntax (use XML validator)
- Verify internal name matches in definition.xml and library section
- Ensure version/dataversion/release match template

**Content doesn't appear**
- Check library section has entries for each content type
- Verify recordname references are correct
- Make sure IDs are unique (id-00001, id-00002, etc.)

**NPCs/Items from other modules don't work**
- Verify the referenced module is loaded in your campaign
- Check the exact recordname format with @ symbol
- Use correct module name (e.g., "Character Law" not "CharacterLaw")

## For Python Scripting

Use these templates as the base structure:
1. Load template_db.xml as a template
2. Populate sections programmatically
3. Replace placeholders in definition.xml
4. Write both files
5. Zip and rename to .mod

See the JSON reference files for data structures:
- `complete_fg_module_structure.json` - Full module structure
- `character_law_npcs.json` - NPC references
- `arms_law_weapons.json` - Weapon references
- Other reference files for items, armor, etc.

---

## Creature and NPC Library

The script includes a built-in library of common MERP creatures and NPCs. You can reference these by name without needing to provide full stats.

### Available Creatures

**Orcs:**
- Orc Scout (Level 6)
- Orc Uruk (Level 8)
- Orc - Bulkupar (Level 10, commander)

**Canines:**
- Wolf (Level 3)
- Wolf - Alpha (Level 5)
- Warg (Level 5)

**Other Monsters:**
- Giant Spider (Level 4)
- Troll (Level 8)

**NPCs from Character Law:**
- Ranger Level 1, 3, 5
- Fighter Level 3, 5

**Custom NPCs:**
- Animist Level 3, 5

### Using Library Creatures

Simply reference by name in your YAML:

```yaml
battles:
  - name: "Orc Ambush"
    exp: 300
    npcs:
      - creature: "Orc Scout"
        count: 3
        faction: foe
```

The script will automatically use all the stats from the library.

### Adding Custom Creatures to the Library

To add new creatures permanently to the library:

1. Open `creature_npc_library.json`
2. Add your creature to the appropriate section (creatures or npcs)
3. Follow this format:

```json
{
  "creatures": {
    "Your Creature Name": {
      "level": 5,
      "hp": 60,
      "at": 10,
      "db": 15,
      "baserate": 50,
      "group": "Monsters",
      "subgroup": "Category",
      "weapons": [
        {
          "name": "Weapon Name",
          "ob": 55,
          "type": "One-Handed Slashing",
          "attack_table": "ALT-22"
        }
      ],
      "defences": [
        {
          "name": "Shield Name",
          "melee_bonus": 20,
          "missile_bonus": 20
        }
      ],
      "abilities": "Special abilities description",
      "description": "Creature description",
      "source": "Book/Module Name"
    }
  }
}
```

### Required Fields

**Minimum required fields:**
- `level` - Creature's level (number)
- `hp` - Hit points (number)
- `at` - Armor Type (number, 1-20)
- `db` - Defensive Bonus (number)
- `weapons` - At least one weapon (array)

**Optional fields:**
- `baserate` - Movement rate (default: 50)
- `group` - "Monsters", "Animals", "NPCs", etc.
- `subgroup` - More specific category
- `defences` - Shields and defensive items (array)
- `abilities` - Special abilities text
- `description` - Flavor text
- `spells` - List of spell lists (for casters)
- `source` - Where the stats came from

### Weapon Format

```json
{
  "name": "Scimitar",
  "ob": 60,
  "type": "One-Handed Slashing",
  "attack_table": "ALT-22"
}
```

**Attack Table IDs:**
See `arms_law_weapons.json` for complete list. Common ones:
- ALT-04: Broadsword
- ALT-22: Scimitar
- ALT-24: Short Sword
- AMT-07: Long Bow
- AMT-08: Short Bow
- APT-04: Quarterstaff/Staff
- CLT-07: Bite (animal)
- CLT-12: Tiny (bite)

### Defence Format

```json
{
  "name": "Normal Shield",
  "melee_bonus": 20,
  "missile_bonus": 20
}
```

### Per-Module Custom Creatures

If you need a creature just for one module without adding it to the library, define it inline:

```yaml
custom_creatures:
  - name: "Unique Boss Monster"
    level: 12
    hp: 200
    at: 15
    db: 30
    baserate: 60
    weapons:
      - weapon: "Great Sword"
        ob: 95
    abilities: "Regeneration, Fire breath"

battles:
  - name: "Boss Fight"
    npcs:
      - creature: "Unique Boss Monster"
        count: 1
```

### Overriding Library Stats

You can override specific stats from library creatures:

```yaml
battles:
  - name: "Elite Orc Patrol"
    npcs:
      - creature: "Orc Scout"
        count: 2
        override:
          hp: 90        # Tougher than normal
          ob: +10       # Better fighters
          db: +5        # Better armor
```

### Attack Table Reference

When creating custom weapons, you need to specify the attack table. These are the standard codes:

**One-Handed Weapons:**
- ALT-01: Armored Fist
- ALT-04: Broadsword
- ALT-07: Dagger
- ALT-22: Scimitar
- ALT-24: Short Sword

**Two-Handed Weapons:**
- ALT-27: Two-handed Sword
- APT-04: Quarterstaff

**Missile Weapons:**
- AMT-07: Long Bow
- AMT-08: Short Bow
- AMT-05: Heavy Crossbow

**Natural Weapons:**
- CLT-03: Claw
- CLT-07: Bite (medium)
- CLT-12: Tiny bite

See `arms_law_weapons.json` for the complete list with all attack tables.

### Tips for Creating Custom Creatures

**HP Calculation (rough guide):**
- Weak creature: 10 + (level × 5)
- Average creature: 15 + (level × 8)
- Tough creature: 20 + (level × 12)

**Armor Type (AT):**
- 1-5: No armor / soft leather
- 6-10: Rigid leather
- 11-15: Chain mail
- 16-20: Plate armor

**Offensive Bonus (OB) rough guide:**
- OB ≈ level × 10 (for trained fighters)
- OB ≈ level × 6-8 (for less martial creatures)

**Defensive Bonus (DB):**
- Usually 0-20 for most creatures
- Shields add 10-25
- Agile creatures might have higher natural DB

These are rough guidelines - consult your MERP/Rolemaster books for official stat blocks to use as reference.
