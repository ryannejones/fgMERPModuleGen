# Complete YAML Generation Instructions for MERP Fantasy Grounds Modules

## Overview
These instructions describe how to extract content from MERP adventure PDFs and create properly structured YAML files for Fantasy Grounds module generation, along with image processing requirements.

## General Principles

### Content Processing Rules
1. **Skip entirely**: Sections 1.0 (Guidelines) and 2.0 (Player Characters)
2. **Process for adventures**: Section 3.0+ until reaching the stats/tables section
3. **Stats/Tables section**: Use as reference for NPC stats, item properties, etc., but don't generate stories or encounters from it
4. **Identify stats section by**: Section titled "Tables" or containing subsections like "Encounter Table", "Beast Table", "NPC Table", "Herb Table", etc.

### Naming Conventions

#### Encounters and Stories (human-readable)
- **Format**: `CC.SS.AA-Name Here`
  - **CC** = Chapter number (zero-padded to 2 digits): `03`, `04`, `05`
  - **SS** = Section number (zero-padded to 2 digits): `00`, `01`, `34`
  - **AA** = Area number (zero-padded to 2 digits, optional): `01`, `02`
- **Area Definition**: Use AA when numbered sections correlate to numbers on a map in that text section
- **When unsure about areas**: Skip AA and combine everything into one story/encounter named `CC.SS-Name Here`
- **Examples**:
  - `"03.00-Attercop Attack"` (main adventure chapter)
  - `"03.34-The Spiders' Lair"` (section with map)
  - `"03.34.01-Clearing"` (specific area on map)
  - `"05.32.01-Keep Entrance"`

#### NPCs (human-readable)
- **Format**: `"Full Name"` (proper capitalization with spaces)
- **Examples**:
  - `"Ulgar Resticsard"`
  - `"Rothaar One-Leg"`
  - `"Grimbold"`
- **Duplicate names**: If two NPCs have the same name, append `" (second)"`, `" (third)"`, etc.
  - `"Tumag"` and `"Tumag (second)"`
- **Rule**: If the PDF lists two NPCs with the same name as separate entities, they get separate entries

#### Items (human-readable with properties)
- **Format**: `"Item Name"` or `"Item Name +Bonus"` or `"Item Name xN Property"`
- **Named items**: Use the proper name: `"Aldataur"`, `"Gihellin's Dagger"`
- **Generic items with bonuses**: Include the bonus in the name
  - `"Broadsword +10"`
  - `"War Hammer +15"`
  - `"Shield +5"`
  - `"Chain Armor +10"`
- **Items with special properties**: Include the property
  - `"Ring x2 Power Points"`
  - `"Dagger +1 Spell Adder"`
- **Descriptive items**: Use clear, specific names
  - `"Axe of Orc-Slaying"`
  - `"Cloak of Hiding +15"`
  - `"Boots of Leaving"`
- **Apostrophes allowed**: `"Gihellin's Dagger"` is correct

#### Images (snake_case derived from encounter/story names)
- **Format**: Convert encounter/story names to snake_case, remove apostrophes and parentheses
  - Spaces → underscores
  - Lowercase all
  - Remove: `'`, `(`, `)`
  - Keep: numbers, periods, underscores
- **Pattern**: `CC.SS.AA_name_here.png`
- **Examples**:
  - `"03.00-Attercop Attack"` → `"03.00_attercop_attack.png"`
  - `"03.34.01-Clearing"` → `"03.34.01_clearing.png"`
  - `"05.32-Ilmaryen Keep"` → `"05.32_ilmaryen_keep.png"`
  - `"Gihellin's Dagger"` → `"gihellins_dagger.png"` (if it had an image)

---

## module.yaml Instructions

**CRITICAL: Generate this file LAST after all other YAML files are complete.**

**CRITICAL WARNING - Output Directory:**
The `output.directory` field must be set to `"./output"` (relative path).
**DO NOT use `/mnt/user-data/outputs` or any absolute path.**
The output directory is relative to where the generator runs, NOT Claude's working directory.

See `yaml_schema.md` for the complete module.yaml schema and required fields.

---

## items.yaml Instructions

### Purpose
Define all items that appear in the module - both magical and mundane. Items must be defined here before they can be referenced in npcs.yaml, parcels.yaml, or stories.yaml.

### Critical Rules
1. **All items must be defined in items.yaml** - even mundane weapons and equipment
2. **Coins do NOT go in items.yaml** - they go in parcels.yaml
3. **Items can be library references or custom creations**

### When to Create Item Entries
Create an item entry for:
1. **All weapons and equipment** used by NPCs (broadsword, long bow, etc.)
2. **Magic items** with special properties
3. **Named items** (e.g., "Aldataur", "Gihellin's Dagger")
4. **Trade goods and supplies** mentioned in parcels
5. **Herbs and consumables** (MERP herbs from Rolemaster Companion)
6. **Special treasures** in hoards

### When NOT to Create Item Entries
Do not create entries for:
1. **Coins and currency** (GP, SP, BP, CP, TP - these go in parcels.yaml)

### Schema Structure

There are three types of item entries:

#### Type 1: Library Item (no modifications)
```yaml
items:
  - name: "Broadsword"
```

#### Type 2: Library Item with Modifications
```yaml
items:
  - name: "Gihellin's Dagger"
    based_on: "Dagger"
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "Old family heirloom originally forged in Gondolin. The enchanted blade glows with a cold blue light when near creatures of Darkness (+5 bonus)."
      notes:
        "@type": "formattedtext"
        "_text": "Glows blue near creatures of Darkness (Orcs, Trolls, Spiders, etc.)"
```

#### Type 3: Fully Custom Item
```yaml
items:
  - name: "Aldataur"
    based_on: ""
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "A 1' long miniature spear made of jet. Named 'Aldataur' (S. 'Commander of the Woods'). Changes size when name is spoken."
```

### Field Descriptions

#### For Library Items (Type 1)
- **name**: Exact name as it appears in Arms Law (e.g., "Broadsword", "Long Bow", "Dagger")

#### For Modified/Custom Items (Type 2 and 3)
- **name**: Human-readable item name (can include bonuses: "Magic Sword +5")
- **based_on**: Name of base item from Arms Law; use `""` (empty string) for fully custom items
- **modifications**: Dictionary of fields to override/add
  - **description**: Item description (use @type and _text structure)
  - **notes**: Additional notes about the item (use @type and _text structure)
  - Other fields can be modified as needed (see generator code for available fields)

### Extraction Process

1. **Scan all adventure sections** for items:
   - NPC equipment (weapons, armor)
   - Treasure descriptions
   - Quest items mentioned in narrative
   - Consumables (herbs, potions)

2. **For each item**:
   - **If it's a standard item from Arms Law** → Add just the name
   - **If it has special properties** → Use based_on + modifications
   - **If it's completely custom** → Use based_on: "" with full modifications

3. **Extract descriptions**:
   - Copy the complete text description from the PDF
   - Extract any special rules or mechanics
   - Note magical properties, bonuses, or limitations

### Examples

```yaml
items:
  # Standard weapons (just names - no modifications needed)
  - name: "Broadsword"
  - name: "Long Bow"
  - name: "Short Sword"
  - name: "Dagger"
  - name: "Scimitar"
  - name: "Battle Axe"
  - name: "Normal Shield"
  
  # MERP Herbs (library items)
  - name: "Carefree Mustard"
  - name: "Tulavar"
  - name: "Kelventari"
  - name: "Mirenna"
  
  # Custom magical items with modifications
  - name: "Gihellin's Dagger"
    based_on: "Dagger"
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "Old family heirloom originally forged in Gondolin. The enchanted blade glows with a cold blue light when near creatures of Darkness (+5 bonus)."
      notes:
        "@type": "formattedtext"
        "_text": "Glows blue near creatures of Darkness (Orcs, Trolls, Spiders, etc.)"
  
  - name: "Inerenerab"
    based_on: "Backpack"
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "Enchanted wooden box constructed by the Woodmen. Measures 12\"x8\"x6\". Keeps herbs fresh for months or stores enough food to feed one person for a month. Given to each PC by the Woodmen."
  
  - name: "Necklace of Deployment"
    based_on: "Opal Necklace"
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "Silver necklace bearing an amber medallion in the form of a compass rose. Worn by Skauril. Allows the wearer to cast Leaving on five creatures at the same time, sending them in up to six different directions."
  
  - name: "Emerald Ring of Elf-friend"
    based_on: "Emerald Ring"
    modifications:
      description:
        "@type": "formattedtext"
        "_text": "Emerald ring given by Thranduil to signify Elf-friend status. Bears no enchantment but is quite valuable and grants recognition among the Elves."
```

### Common Modification Patterns

#### Adding Description
```yaml
modifications:
  description:
    "@type": "formattedtext"
    "_text": "Your description here"
```

#### Adding Notes
```yaml
modifications:
  notes:
    "@type": "formattedtext"
    "_text": "Special rules or properties"
```

#### Both Description and Notes
```yaml
modifications:
  description:
    "@type": "formattedtext"
    "_text": "Item appearance and history"
  notes:
    "@type": "formattedtext"
    "_text": "Game mechanics and special properties"
```

### Important Notes

1. **Always use the @type and _text structure** for formatted text fields
2. **@type should always be "formattedtext"** for descriptions and notes
3. **Empty based_on** uses empty string `""`, not omitting the field
4. **Exact names matter** - "Broadsword" must match Arms Law exactly
5. **Don't invent modifications** - if uncertain about a base item, leave based_on empty and ask
6. **All NPC weapons** must exist in items.yaml (even if just a name entry)

---

## npcs.yaml Instructions

### Purpose
Define all named NPCs that appear in the adventure. These NPCs can then be referenced in encounters and stories. NPCs are built based on library creatures/templates (from Character Law) with modifications.

### When to Create NPC Entries
Create an entry for:
1. **Named individuals** with unique stats or modifications (e.g., "Skauril the Conjurer", "Natak")
2. **Modified generic types** used in encounters (e.g., custom "Orc Warrior" with specific stats)
3. **NPCs that need special equipment or abilities** beyond library defaults
4. **ALL creatures used in encounters** - every creature needs at least a minimal entry

**CRITICAL RULE:** Every creature referenced in `encounters.yaml` MUST have a corresponding entry in `npcs.yaml`. No exceptions. Even library creatures used without modifications need a minimal entry like:
```yaml
- name: "Wolf"
  based_on: "Wolf"
```

### When NOT to Create NPC Entries
Do not create entries for:
1. **Player Characters** from section 2.0 (those are pre-gens for players)
2. **NPCs only mentioned in narrative** that don't appear in encounters

### Duplicate Name Handling
- If the PDF text explicitly indicates separate individuals (e.g., "Tumag and Tumag are twin brothers" or "the second Korlagz-drartul"), create separate NPC entries with "(second)", "(third)", etc. appended to the name
- If the same name appears multiple times WITHOUT explicit indication of separate individuals, it's the SAME NPC - create only ONE entry
- Look for textual clues like: "both named X", "twin brothers both called X", "the other X", "the second X"

### Schema Structure

```yaml
npcs:
  - name: "NPC Name"
    based_on: "Library Creature/Template Name"
    level: 10
    hp: 35
    at: 2
    db: 0
    baserate: 50
    race: "Race"
    group: "NPCs" | "Monsters"
    weapons:
      - weapon: "Weapon Name"
        ob: 20
    defences:
      - name: "Defense Item Name"
        melee_bonus: 10
        missile_bonus: 10
    abilities: "Special abilities, spells, skills"
    stats: "Stat line (Co, Ag, SD, etc.)"
    description: "Physical appearance and personality"
```

### Field Descriptions

#### Required Fields
- **name**: Human-readable NPC name (unique identifier)
- **based_on**: Name of base creature from library (e.g., "Pure Essence Spell User", "Orc, Lesser", "Orc (leader)", "Fighter", "Ranger")

#### Commonly Used Optional Fields
- **level**: Character level (integer)
- **hp**: Hit points (overrides library default)
- **at**: Armor type (integer, RM armor type number)
- **db**: Defensive bonus (integer)
- **baserate**: Base movement rate (usually 50 or 60)
- **race**: Character's race (Human, Elf, Orc, etc.)
- **group**: "NPCs" for humanoids, "Monsters" for creatures
- **weapons**: List of weapons with offensive bonuses
- **defences**: List of defensive items (shields, armor) with bonuses
- **abilities**: Special abilities text (simple string)
- **spells**: Spell lists and levels text (simple string)
- **stats**: Full stat line if needed (simple string)
- **description**: Physical appearance and personality (simple string)

### Extraction Process

1. **Identify named NPCs** in adventure sections (3.0+)
2. **Check if NPC has stats in the tables section** (usually section 6.x)
3. **For each NPC**:
   - Determine the base creature type (what library entry is closest)
   - Extract level and any stat modifications
   - Extract weapons and equipment
   - Extract special abilities from narrative
   - Write physical and personality description from narrative

### Weapon Format
```yaml
weapons:
  - weapon: "Broadsword"  # Must exist in items.yaml
    ob: 110             # Offensive bonus
  - weapon: "Long Bow"
    ob: 75
```

### Defence Format
```yaml
defences:
  - name: "+10 Chain Shirt"
    melee_bonus: 10
    missile_bonus: 10
  - name: "Normal Shield"
    melee_bonus: 0
    missile_bonus: 0
```

### Examples

```yaml
npcs:
  # Named major NPC with custom stats
  - name: "Skauril the Conjurer"
    based_on: "Pure Essence Spell User"
    level: 10
    hp: 35
    at: 2
    db: 0
    baserate: 50
    race: "Easterling"
    group: "NPCs"
    weapons:
      - weapon: "Short Sword"
        ob: 20
      - weapon: "Short Bow"
        ob: 15
    abilities: "Lieutenant to Khamûl the Easterling. Necklace of Deployment, Ring of Shielding. Commands army of 500+ Orcs and Men."
    spells: "Fire law, Water law, Wind law, Light law, Earth law, Ice law, Lofty Bridge, Living Change, Spirit Mastery, Spell Ways, Unbarring Ways, Directed Spells (all to 10th level). Animal Handling 45, Animal Healing 15."
    stats: "Co86, Ag81, SD35, Me97, Re98, St74, Qu72, Pr63, Em100, In87"
    description: "Lieutenant of the Witch-king. Commands assault on Thranduil's Elves. Crafty, experienced, but values own life above all. Will abandon army to save himself."
  
  # Named NPC with equipment
  - name: "Natak"
    based_on: "Orc, Greater"
    level: 5
    hp: 76
    at: 20
    db: 20
    baserate: 50
    group: "Monsters"
    weapons:
      - weapon: "Throwing Hammer"
        ob: 90
      - weapon: "Long Bow"
        ob: 50
    defences:
      - name: "+10 Plate Armor with Horned Drake Helm"
        melee_bonus: 10
        missile_bonus: 10
    abilities: "Commander of Skauril's Orcs at the battle of the Gladuin. Wields 'Reaver' +15 two-handed sword of slaying Dwarves. Darkvision."
    stats: "Co96, Ag85, SD71, Me74, Re78, St93, Qu81, Pr91, Em65, In80"
    description: "Largest and most brutal of the Uruks. Commands through fear and terror. His own troops fear him more than the enemy."
  
  # Custom creature type used in encounters
  - name: "Orc Warrior"
    based_on: "Orc, Lesser"
    level: 3
    hp: 45
    at: 9
    db: 35
    baserate: 50
    weapons:
      - weapon: "Scimitar"
        ob: 60
      - weapon: "Battle Axe"
        ob: 40
    defences:
      - name: "Shield"
        melee_bonus: 0
        missile_bonus: 0
    abilities: "Low steel weapons. Form the core of Skauril's orc forces."
    description: "Lesser orcs pressed into service. Fight better than expected due to fear of their commanders."
  
  # Simple reference - library creature used with minimal modifications
  - name: "Scout"
    based_on: "Fighter"
    level: 3
    hp: 40
    at: 4
    db: 20
    baserate: 50
    race: "Common Man"
    weapons:
      - weapon: "Dagger"
        ob: 65
      - weapon: "Dagger"
        ob: 50
    abilities: "+30 Detect Traps. Steel weapons."
    description: "Skilled scouts in Skauril's army. Used for reconnaissance and trap detection."
  
  # Minimal entry - just references library with level
  - name: "Animist"
    based_on: "Pure Channeling Spell User"
    level: 5
  
  # Another minimal entry
  - name: "Ranger"
    based_on: "Ranger"
    level: 5
  
  # Library creature reference
  - name: "Orc Scout"
    based_on: "Orc, Lesser"
  
  - name: "Giant Spider"
    based_on: "Giant Spider"
  
  - name: "Warg"
    based_on: "Warg"
  
  - name: "Wolf"
    based_on: "Wolf"
  
  - name: "Stone Troll"
    based_on: "Stone Troll"
```

**Note:** Even for library creatures used without modifications, create minimal entries like the last few examples above. This is required for validation.

### Base Creature References

Common library creatures to use as `based_on`:
- **"Pure Essence Spell User"** - for wizards/sorcerers
- **"Pure Channeling Spell User"** - for animists/clerics
- **"Fighter"** - for warriors
- **"Ranger"** - for rangers
- **"Rogue"** - for thieves/scouts
- **"Orc, Lesser"** - for orc scouts/warriors
- **"Orc, Greater"** - for uruk warriors
- **"Orc (leader)"** - for orc leaders/uruks
- **"Giant Spider"** - for spiders
- **"Warg"** - for wargs
- **"Stone Troll"** - for trolls

### Important Notes

1. **based_on is always required** - even if empty string `""`
2. **All weapons must exist in items.yaml** first
3. **Minimal entries are fine** - just name, based_on, and level if needed
4. **Description is optional** - add when there's narrative text about the NPC
5. **Stats are optional** - only include modifications from the base creature
6. **hp, at, db are direct overrides** - not modifications to base values

---

## encounters.yaml Instructions

### Purpose
Define specific combat encounters or significant NPC meetings within each adventure. These encounters are referenced by stories to provide combat statistics and NPC groupings.

### When to Create Encounter Entries
Create an encounter for:
1. **Specific combat scenarios** described in the adventure (e.g., "The Spiders", "The Troll Band")
2. **Groups of enemies** at specific locations (e.g., "Orcs at Ilmaryen Keep")
3. **Significant NPC meetings** that might lead to combat or important interaction

### When NOT to Create Encounter Entries
Do not create encounters for:
1. **Random encounter tables** (section 6.x content)
2. **Generic travel encounters** not specific to the adventure
3. **Individual NPCs** already defined in npcs.yaml (reference them directly in stories)

### Schema Structure

```yaml
encounters:
  - name: "CC.SS.AA-Encounter Name"
    description: "Description of the encounter setup, enemy tactics, and circumstances"
    npcs:
      - "NPC Name 1"
      - "NPC Name 2"
    enemies:
      - type: "Creature Type"
        count: 5
        level: 3
        stats: "Brief stat block or reference to creature stats"
    treasure: "Description of any treasure obtained from this encounter"
    notes: "Tactical information, special circumstances, or conditional triggers"
```

### Field Descriptions

#### Required Fields
- **name**: Encounter identifier using naming convention (CC.SS.AA-Name)
- **description**: Setup and context for the encounter

#### Optional Fields
- **npcs**: List of NPC names from npcs.yaml who participate in this encounter
- **enemies**: List of enemy groups (for generic/unnamed creatures)
  - **type**: Creature type (e.g., "Lesser Orc Warrior", "Giant Spider", "Stone Troll")
  - **count**: Number of this type of creature
  - **level**: Average level of creatures
  - **stats**: Brief stat reference or "See Beast Table" or "See NPC Table"
- **treasure**: Description of loot from this encounter
- **notes**: Additional tactical, environmental, or conditional information

### Extraction Process

1. **Read each adventure section** (3.0, 4.0, 5.0, etc.)
2. **Identify named encounter sections**:
   - Look for subsections titled "Encounters" 
   - Look for section headers describing specific fights or meetings
   - Look for locations with named enemy groups
3. **For each encounter**:
   - Use the section numbering to create the name (CC.SS or CC.SS.AA)
   - Extract the narrative description of the encounter setup
   - List all named NPCs involved (must be in npcs.yaml)
   - List generic enemy types with counts and levels
   - Note any treasure specifically associated with this encounter
   - Extract tactical notes, special conditions, or triggers

### Examples

```yaml
encounters:
  - name: "03.05-The Spiders"
    description: "Five Giant Spiders reside in this web complex. All have eaten well recently, so they will probably (01-85) all be in their lair. If not, two will always be there; the others will be out hunting in a single group consisting of one (01-25), two (26-70), or three (71-00) individuals. The Spiders, when in their lair, generally occupy the northwesternmost portion, either over the refuse pile or within 20' of the captives. They will immediately and unhesitatingly attack any creature entering their domain. Their favorite tactic is to send 1-3 Spiders (depending on how many are present and how great the threat) in a frontal assault while the remainder divide and circle to attack both flanks and/or the rear of their foes."
    enemies:
      - type: "Giant Spider"
        count: 5
        level: 8
        stats: "See Beast Table 6.2"
    treasure: "In refuse pile (area 4): belt of brass rings (+10 DB); magic emerald (15th-level lifegiving spell, 1 use only); beautifully crafted morningstar (60% lighter than normal, casts MERP Wind Law Air Wall 1x/day); small locked chest containing 24 gp, 64 sp, 360 bp, 550 cp, 450 tp; velvet pouch with 16 gp, 40 sp, and 2 gems (10 gp moonstone, 25 gp aquamarine); silver ring (15 sp); gold armband set with garnets (120 gp)."
    notes: "If any Spiders are out hunting, there is a slim chance (01-10) they are between the lair and the road. They will most likely have travelled north or west to hunt. To determine that Spiders are missing from the lair and the number gone, characters must make a Hard (-20) Perception roll."

  - name: "04.05-The Trolls"
    description: "The Trolls' tracks leave the Road and lead directly north from the site of the ambush. Four Stone Trolls live in the cave and have taken the merchant's wagon with them. The Trolls can be encountered either inside their lair or outside at night. By daylight, all four Trolls will be in their caves, though one might be awake on guard. At night, the Trolls are frequently out on business, smashing, breaking, murdering, destroying, and terrorizing the countryside."
    npcs:
      - "Fradurag"
      - "Tumag"
      - "Tumag (second)"
      - "Umik"
    treasure: "See treasure descriptions in areas 8, 9, and 10 of the Troll Lair."
    notes: "The Trolls may seek amusement singly or in groups. Use the Nocturnal Troll Encounters table to determine how many Trolls are present in various circumstances. Trolls are -20 to all actions during daylight even in their darkened cave. If they step into direct sunlight (very unlikely) they will be instantly turned to stone."

  - name: "05.00-The Tithing Train"
    description: "The Orcs garrisoning Ilmaryen Keep can be encountered either inside or outside the keep. The garrison consists of thirty Orcs organized into six Korlagzrim (squads of five). Two Korlagzrim are Uruk-level, four are Lesser Orcs. They maintain an organized watch system with one Korlagz on duty at a time. During the day, two Orcs watch in the Gatehouse while three remain in the Great Hall. At night, two Orcs guard each tower roof while one (the Korlagz-drartul) patrols between the Upstairs Corridor and Great Hall."
    npcs:
      - "Yagrash"
      - "Marlurg"
      - "Ukrish"
      - "Gormuk"
      - "Bokdankh"
      - "Skoralg"
      - "Fektalgh"
      - "Hagrakh"
    enemies:
      - type: "Lesser Orc Kragashi"
        count: 16
        level: 1-2
        stats: "See NPC Table 6.4"
      - type: "Uruk Kragashi"
        count: 8
        level: 2-3
        stats: "See NPC Table 6.4"
    treasure: "Extensive treasure hoards in area 21 (Treasure Room) and scattered throughout NPC quarters. See individual area descriptions for details."
    notes: "Almost half the time (01-40), 1-3 Korlagzrim not on guard duty will be out raiding at night. The keep doors will be open at night unless an alarm has been sounded. During the day, Lesser Orcs are -65 to all activity and avoid light; Uruks do not fear sun as much. Watch rotation ensures each Korlagz has one day in six off duty."

  - name: "03.34.05-Captives"
    description: "Two vaguely human-shaped cocoons are hanging in the webs, fifteen feet off the ground, at this location. If the cocoons are carefully cut open, they will reveal Runnal and Currael. Both are in very poor shape. They can barely walk and will be of no help to the party, but each will insist on saving the other. The Spiders are most commonly found in this area of the web when they aren't away hunting."
    npcs:
      - "Runnal Resticsard"
      - "Currael Wessuntha"
    notes: "Runnal and Currael are -60 to all activities due to weakness and wounds from Spider venom. They must be rescued as part of the adventure objectives. Each is worth 50 gp reward for safe return."
```

### Notes on Extraction

1. **Encounter naming**: Use the section number where the encounter is described. If it's in a subsection called "Encounters", use that section's number. If it's a specific area with enemies, use the area number.

2. **Named vs. Generic enemies**: 
   - If enemies have individual names and stat blocks, list them in npcs
   - If enemies are generic groups ("5 spiders", "16 lesser orcs"), use the enemies list
   - You can have both in the same encounter

3. **Stats reference**: For generic enemies, reference the appropriate table:
   - "See Beast Table 6.2" for creatures
   - "See NPC Table 6.4" for humanoid enemies
   - Include the actual reference section if available

4. **Treasure**: Only include treasure specifically from defeating this encounter. Don't include treasure found in the location that's unrelated to the enemies.

5. **Tactical notes**: Extract important information about:
   - Enemy tactics and behavior
   - Special conditions or triggers
   - Time-of-day variations
   - Environmental factors
   - Win conditions or objectives

6. **Multiple encounter types**: If a location can have different encounter configurations (like the Trolls being inside or outside), describe the variations in the description and notes.

---

## parcels.yaml Instructions

### Purpose
Define treasure parcels containing coins and items. Parcels represent loot from encounters, treasure hoards, quest rewards, or starting equipment.

### When to Create Parcel Entries
Create a parcel for:
1. **Encounter loot** - treasure from defeating enemies
2. **Treasure hoards** - caches found in locations
3. **Quest rewards** - items given by NPCs
4. **Starting equipment** - gear provided to PCs at adventure start

### Critical Rules
1. **Coins go ONLY in parcels** - never in items.yaml
2. **All items referenced must exist in items.yaml** first
3. **Parcels embed item data** - the generator copies full item definitions into the parcel

### Schema Structure

```yaml
parcels:
  - name: "Parcel Name"
    description: "Description of the treasure and its context"
    coins:
      MP: 0   # Mithril Pieces
      PP: 0   # Platinum Pieces
      GP: 50  # Gold Pieces
      SP: 120 # Silver Pieces
      BP: 0   # Bronze Pieces
      CP: 0   # Copper Pieces
      TP: 0   # Tin Pieces
      IP: 0   # Iron Pieces
    items:
      - name: "Item Name"  # Must exist in items.yaml
        count: 1
      - name: "Another Item"
        count: 3
```

### Field Descriptions

#### Required Fields
- **name**: Parcel identifier (use section numbering: "6.5.02 - Bridge Crew Loot")

#### Optional Fields
- **description**: Context about where/how this treasure is obtained
- **coins**: Dictionary of coin types and amounts (omit types with 0 value)
- **items**: List of items with counts

### Coin Types

All coin types are optional - only include types that have non-zero amounts:
- **MP**: Mithril Pieces (most valuable)
- **PP**: Platinum Pieces
- **GP**: Gold Pieces (standard)
- **SP**: Silver Pieces
- **BP**: Bronze Pieces
- **CP**: Copper Pieces
- **TP**: Tin Pieces
- **IP**: Iron Pieces (least valuable)

### Item Format

Items in parcels use the same format:
```yaml
items:
  - name: "Broadsword"  # Must match name in items.yaml exactly
    count: 6
  - name: "Gihellin's Dagger"
    count: 1
```

### Extraction Process

1. **Identify treasure locations** in adventure text:
   - Encounter sections (e.g., "6.5.02 - Bridge Crew")
   - Room descriptions with treasure
   - NPC equipment that becomes loot
   - Quest reward descriptions

2. **For each treasure**:
   - Create a parcel with section-numbered name
   - Extract coin amounts from text
   - Extract item names and quantities
   - Verify all items exist in items.yaml
   - Add description about context/location

3. **Combine or separate parcels**:
   - One parcel per encounter is typical
   - Separate parcels for different locations in the same encounter if appropriate
   - Quest rewards are usually separate parcels

### Examples

```yaml
parcels:
  # Encounter loot
  - name: "6.5.02 - Bridge Crew Loot"
    description: "Equipment and supplies from the defeated bridge crew"
    coins:
      GP: 50
    items:
      - name: "Broadsword"
        count: 6
      - name: "Long Bow"
        count: 4
      - name: "Dagger"
        count: 6
  
  # Treasure with multiple coin types
  - name: "6.5.03 - Road Crew Loot"
    description: "Loot from defeated road crew. Orcish equipment is crude and of poor quality."
    coins:
      GP: 15
      SP: 30
    items:
      - name: "Scimitar"
        count: 10
  
  # Quest reward
  - name: "6.6.01 - Spoils of Gulduin"
    description: "Thranduil's share of battle spoils offered to the PCs. Includes Elven cloak (grants +10 to Hiding in forest), bottle of Elven cordial (heals 1-10 HP), silver dagger (+5, non-magical but fine quality), and choice of weapon from Elven armory."
    coins:
      GP: 200
    items:
      - name: "Emerald Ring of Elf-friend"
        count: 1
      - name: "Dagger"
        count: 1
  
  # Starting equipment
  - name: "6.0.01 - Starting Equipment from Woodmen"
    description: "Supplies provided by the Woodmen before departure. Includes 50 feet of rope, waterskins (full), fire-starting kit, and map drawn by Gihellin."
    items:
      - name: "Inerenerab"
        count: 1
      - name: "Gihellin's Dagger"
        count: 1
      - name: "Carefree Mustard"
        count: 3
      - name: "Kelventari"
        count: 4
      - name: "Mirenna"
        count: 6
      - name: "Tulavar"
        count: 2
  
  # Large treasure hoard
  - name: "05.32.21 - Treasure Room"
    description: "Vast treasure chest from Ilmaryen Keep. Contains coins and magical items."
    coins:
      GP: 562
      SP: 2205
      BP: 6229
      CP: 8896
      TP: 11624
    items:
      - name: "Shield +20 Invisibility"
        count: 1
      - name: "Garnet of Hues"
        count: 1
      - name: "Aldataur"
        count: 1
```

### Common Patterns

#### Pattern 1: Simple Encounter Loot
```yaml
- name: "3.05 - Spider Lair Treasure"
  description: "Found in refuse pile under spider webs"
  coins:
    GP: 24
    SP: 64
  items:
    - name: "Morning Star +10"
      count: 1
```

#### Pattern 2: NPC Equipment as Loot
```yaml
- name: "4.05 - Troll Leader Equipment"
  description: "Fradurag's possessions"
  items:
    - name: "Battleaxe +5"
      count: 1
    - name: "Ring of Spell Defense"
      count: 1
```

#### Pattern 3: Mixed Treasure
```yaml
- name: "5.32.08 - Orc Quarters"
  description: "Personal belongings of garrison orcs"
  coins:
    SP: 15
    CP: 40
  items:
    - name: "Scimitar"
      count: 3
```

### Handling Non-Item Treasures

The description field can mention items that don't need mechanical stats:
```yaml
- name: "6.5.04 - Scouting Party Loot"
  description: "Equipment from the scouting party. Tracking equipment of excellent quality, signal horn (orcish make), map fragment showing Skauril's route (if not destroyed)."
  coins:
    GP: 25
  items:
    - name: "Scimitar"
      count: 5
    - name: "Long Bow"
      count: 4
```

### Important Notes

1. **Validation**: Generator will fail if items don't exist in items.yaml
2. **Exact names**: Item names must match items.yaml exactly (case-sensitive)
3. **Count defaults to 1**: If count is omitted, it's assumed to be 1
4. **Zero coins**: Omit coin types that are 0 (cleaner YAML)
5. **Description is important**: Tells GMs when/how players get this treasure

---

## stories.yaml Instructions

### Purpose
Create story entries for adventure sections, providing narrative text, room descriptions, and organizational structure for the module. Stories can reference encounters, NPCs, items, parcels, and images through hyperlinks.

### When to Create Story Entries
Create stories for:
1. **Main adventure chapters** (e.g., "6.0.01 - Introduction to Skauril's Army")
2. **Major sections within adventures** (e.g., "6.1.01 - The Plotting of Skauril")
3. **Individual areas/rooms** with descriptions (e.g., "6.5.02 - Bridge Crew Encounter")
4. **Significant plot points or scenes** (e.g., "6.2.01 - NPC: Gardagd")

### Story Entry Hierarchy
- **Chapter level** (X.0.01): Overview of entire adventure or major introduction
- **Section level** (X.X.01): Major locations, plot points, or NPC introductions
- **Area level** (X.X.02, X.X.03, etc.): Individual encounters, rooms, or specific locations

### Schema Structure

```yaml
stories:
  - name: "Story Name"
    sections:
      - type: "header"
        text: "Section Title"
      
      - type: "gm_notes"
        text: "Information for the GM"
      
      - type: "read_aloud"
        text: "Text to read aloud to players"
      
      - type: "link_encounter"
        encounter_name: "Encounter Name"
        link_text: "Optional display text"
      
      - type: "link_npc"
        npc_name: "NPC Name"
        link_text: "Optional display text"
      
      - type: "link_item"
        item_name: "Item Name"
        link_text: "Optional display text"
      
      - type: "link_parcel"
        parcel_name: "Parcel Name"
        link_text: "Optional display text"
      
      - type: "link_image"
        image_name: "Image Name"
        link_text: "Optional display text"
```

### Field Descriptions

#### Required Fields
- **name**: Story identifier (human-readable, can use section numbering)
- **sections**: List of sections (at least one section required)
- **sections[].type**: Section type (see types below)

#### Section Types and Required Fields

**Text Section Types:**
- **header**: Section title
  - Required: `text` - The header text
- **read_aloud**: Text for players
  - Required: `text` - Text meant to be read aloud
- **gm_notes**: GM information
  - Required: `text` - Information for GM only

**Link Section Types:**
- **link_encounter**: Link to an encounter
  - Required: `encounter_name` - Name of encounter from encounters.yaml
  - Optional: `link_text` - Display text (defaults to "Encounter: {name}")
- **link_npc**: Link to an NPC
  - Required: `npc_name` - Name of NPC from npcs.yaml or library
  - Optional: `link_text` - Display text (defaults to "NPC: {name}")
- **link_item**: Link to an item
  - Required: `item_name` - Name of item from items.yaml
  - Optional: `link_text` - Display text (defaults to "Item: {name}")
- **link_parcel**: Link to a treasure parcel
  - Required: `parcel_name` - Name of parcel from parcels.yaml
  - Optional: `link_text` - Display text (defaults to "Treasure: {name}")
- **link_image**: Link to an image/map
  - Required: `image_name` - Name of image from images
  - Optional: `link_text` - Display text (defaults to "Map: {name}")

### Determining Section Type

Use this decision tree for each paragraph:

1. **Is it a section title or header?** → `header`
2. **Would this be read aloud to describe a scene?** → `read_aloud`
   - Physical descriptions of locations
   - Visible features of rooms or areas
   - NPC appearances when first encountered
   - Atmospheric descriptions
   - Things players can observe
3. **Is it mechanical information or hidden details?** → `gm_notes`
   - Stat blocks and game mechanics
   - Hidden features or secrets
   - NPC tactics and strategies
   - Treasure lists
   - Trap mechanics
   - DCs and skill check requirements
   - Background information players shouldn't know
4. **Does it reference another entity?** → `link_*` type
   - Important encounters
   - Key NPCs
   - Significant items
   - Treasure parcels
   - Maps or images
5. **When uncertain about text** → `gm_notes`

### Examples

```yaml
stories:
  - name: "6.0.01 - Introduction to Skauril's Army"
    sections:
      - type: header
        text: "Chapter 6: Skauril's Army - Assault on the Elves"
      
      - type: gm_notes
        text: "This adventure assumes the PCs recovered the scroll from Bulkupar in Chapter 5. If not, another messenger can bring warning to the Woodmen."
      
      - type: read_aloud
        text: "The Woodmen examine the scroll with grave concern. Waulfa looks up from the parchment, his weathered face showing rare alarm. 'Skauril marches against the Elves. We must warn Thranduil, but his warriors are scattered. Someone must slow this army, or many Elves will die.'"

  - name: "6.1.02 - The Request for Aid"
    sections:
      - type: header
        text: "The Task"
      
      - type: read_aloud
        text: "Gihellin the Elf steps forward. 'I will carry word to Thranduil with all haste, but my people are scattered throughout the forest. The house guard alone cannot stop this army.' Waulfa nods gravely. 'If someone could slow the army, track its numbers, or demoralize its troops, the Elves would have time to gather their strength.'"
      
      - type: gm_notes
        text: "If the PCs agree to scout and delay Skauril's army, the Woodmen will provide: reasonable supplies, healing herbs, and Inereneraban for each PC."
      
      - type: link_item
        item_name: "Inerenerab"
        link_text: "Item: Inerenerab (Enchanted Food Box)"
      
      - type: link_item
        item_name: "Gihellin's Dagger"

  - name: "6.2.01 - NPC: Gardagd"
    sections:
      - type: header
        text: "Gardagd - The Bitter Hunter"
      
      - type: gm_notes
        text: "Born to a Gramuz family in the East Bight. At age 10, his father contracted a wasting disease. Returning from one hunt, he found smoldering ruins: father dead, mother and sisters carried off by Easterlings. He became a bandit and was enrolled by Skauril as a scout/assassin. Gardagd secretly hates Easterlings and will kill Skauril if given an easy opportunity."
      
      - type: link_npc
        npc_name: "Gardagd"
        link_text: "NPC: Gardagd Stats"

  - name: "6.3.01 - The Journey to Intercept"
    sections:
      - type: header
        text: "Setting Out"
      
      - type: read_aloud
        text: "You set out into the dark eaves of Mirkwood, following Gihellin's map toward the trail Skauril's army must take. The forest grows darker as you travel deeper, the canopy overhead blocking much of the sun."
      
      - type: gm_notes
        text: "The PCs must locate Skauril's army and begin their delaying actions. The army moves approximately 15 miles per day on the trail. For each day the PCs delay the army, the Elves can muster more warriors."
      
      - type: link_encounter
        encounter_name: "6.5.01 - Locating the Army"

  - name: "6.5.02 - Bridge Crew Encounter"
    sections:
      - type: header
        text: "The Bridge Crew"
      
      - type: gm_notes
        text: "The bridge crew consists of 6 mounted men led by a ranger and an animist. They are scouting ahead to identify river crossings."
      
      - type: link_encounter
        encounter_name: "6.5.02 - Bridge Crew"
      
      - type: link_parcel
        parcel_name: "6.5.02 - Bridge Crew Loot"
```

### Extraction Process

1. **Identify story structure** by reading through adventure sections
2. **Create chapter-level stories** for main introductions (X.0.01)
3. **Create section-level stories** for major locations/plot points (X.X.01)
4. **Create encounter/area stories** for specific locations (X.X.02, X.X.03)
5. **For each story**:
   - Extract all relevant text from the PDF section
   - Break into logical chunks (paragraphs)
   - Classify each chunk by type (header/read_aloud/gm_notes)
   - Add link sections for important references
   - Use `link_text` when you want custom display text

### Notes on Story Creation

1. **Story names**: Use descriptive names with section numbers
   - "6.0.01 - Introduction to Skauril's Army"
   - "6.2.01 - NPC: Gardagd"
   - "6.5.02 - Bridge Crew Encounter"

2. **Section order**: 
   - Headers first
   - Then narrative (read_aloud/gm_notes)
   - Then links at the end

3. **Text multiline**: Use YAML multiline for longer text:
```yaml
- type: gm_notes
  text: |
    First paragraph of GM notes.
    
    Second paragraph with more details.
```

4. **Link placement**: Add links after describing what they reference:
```yaml
- type: gm_notes
  text: "The PCs will encounter Gardagd on the road."

- type: link_npc
  npc_name: "Gardagd"
```

5. **Optional link_text**: Omit if the default is fine:
```yaml
# This will show as "NPC: Gardagd"
- type: link_npc
  npc_name: "Gardagd"

# This will show custom text
- type: link_npc
  npc_name: "Gardagd"
  link_text: "Gardagd the Bitter Hunter"
```

6. **When to link**:
   - Link major NPCs when first introduced
   - Link encounters that might occur in this story
   - Link special items mentioned
   - Link treasure parcels players can find
   - Link maps that illustrate the area

7. **When NOT to link**:
   - Don't link every mention of an NPC, only significant ones
   - Don't link common items unless they're special
   - Don't over-link - it clutters the story

---

## Image Processing Instructions

### Purpose
Extract maps, NPC portraits, and other illustrations from the PDF for use in the Fantasy Grounds module.

### Required Tools

Install `poppler-utils` for PDF image extraction:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

### Image Extraction Process

#### Step 1: Extract All Images from PDF
```bash
# Create images directory
mkdir -p images

# Extract all images from PDF (preserves formats)
pdfimages -all your_module.pdf images/temp_

# This creates files like: temp_000.png, temp_001.jpg, etc.
```

#### Step 2: Review and Select Images

1. **View extracted images** to identify which ones to keep
2. **Determine image types**:
   - Maps (terrain maps, building layouts, area maps)
   - NPC portraits
   - Item illustrations
3. **Skip unwanted images**:
   - Page decorations
   - Publisher logos
   - Section dividers without content

#### Step 3: Rename Images According to Conventions

Rename images using the snake_case format derived from story/encounter names:

```bash
# Examples of renaming:
mv images/temp_003.png images/03.00_attercop_attack.png
mv images/temp_005.png images/03.34_spiders_lair.png
mv images/temp_012.png images/ulgar_resticsard.png
mv images/temp_020.png images/05.32_ilmaryen_keep_cellars.png
mv images/temp_021.png images/05.32_ilmaryen_keep_first_level.png
```

#### Step 4: Create Thumbnail

Extract page 1 as the module thumbnail:
```bash
# Extract first page as PNG at 300 DPI
pdftoppm -png -f 1 -l 1 -singlefile -scale-to 800 your_module.pdf thumbnail

# This creates thumbnail.png - ensure it's in module root, NOT in images/
# The file should be in the root directory, not images/ subdirectory
```

**CRITICAL: Thumbnail Location**
- Thumbnail MUST be named `thumbnail.png` (not `cover.jpg` or `cover.png`)
- Thumbnail MUST be in the **root directory** of your module
- Thumbnail should NOT be in the `images/` subdirectory
- Recommended size: 800 pixels wide (maintains aspect ratio)

If you have `cover.jpg` in `images/`, move and rename it:
```bash
# If you have images/cover.jpg, convert and move it:
convert images/cover.jpg -resize 800x thumbnail.png
# Or if it's already PNG:
convert images/cover.png -resize 800x thumbnail.png
```

### General Rules

1. **First page (cover)**: Extract as `thumbnail.png` in module root directory
2. **Last page**: Skip entirely (usually product listing or ads)
3. **Second-to-last page**: Skip entirely (usually product listing or ads)
4. **Sections 1.0 and 2.0**: Skip all images from these sections
5. **Section 6.0 (Tables)**: Skip all images from the tables section
6. **Sections 3.0+**: Extract all maps and NPC portraits until reaching tables section

### Image Capture Guidelines

1. **Include image borders**: Capture decorative borders that are part of the image itself
2. **Exclude page borders**: Do not capture page numbers, headers, footers, or page margins
3. **When uncertain**: Err on the side of capturing the image with more context
4. **Clean crop**: Images from `pdfimages` are usually pre-cropped, but verify

### Image Types to Extract

1. **Maps**:
   - Area overview maps (like "Mirkwood Area Map")
   - Terrain maps (like "Terrain Map: On the Trail of the Trolls")
   - Location maps (like "The Spiders' Lair")
   - Building floor plans (like "Ilmaryen Keep")
   - Tactical maps showing encounter areas

2. **NPC Portraits**:
   - Character illustrations (like portraits of Ulgar, Currael, Grimbold)
   - Creature illustrations (if shown separately from maps)

3. **Item Illustrations**:
   - Weapon illustrations
   - Magical item illustrations
   - Only if shown as separate detailed images

### Multi-Level Map Handling

When a single page contains multiple map levels (like floor plans of a multi-story building):

1. **If `pdfimages` separates them**: Rename each appropriately
2. **If they're in one image**: You may need to manually crop/split them using an image editor

**Naming for multi-level maps:**
```
05.32_ilmaryen_keep_cellars.png
05.32_ilmaryen_keep_first_level.png
05.32_ilmaryen_keep_second_level.png
05.32_ilmaryen_keep_tower_roofs.png
```

### Image Naming Convention

Convert the story/encounter name to snake_case:

1. **Start with story name**: `"CC.SS.AA-Name Here"`
2. **Convert to lowercase**: `"cc.ss.aa-name here"`
3. **Replace spaces with underscores**: `"cc.ss.aa-name_here"`
4. **Remove apostrophes**: `"gihellins_dagger"` not `"gihellin's_dagger"`
5. **Remove parentheses**: `"tumag_second"` not `"tumag_(second)"`
6. **Add .png extension**: `"cc.ss.aa-name_here.png"`

But keep the section number format with periods:
- `"03.34_spiders_lair.png"` (keep periods in section number)
- `"05.32.01_keep_entrance.png"` (keep periods in section and area numbers)

### Examples

```
Story/Encounter Name              →  Image Filename
"03.00-Attercop Attack"          →  03.00_attercop_attack.png
"03.34-The Spiders' Lair"        →  03.34_spiders_lair.png
"04.32-The Troll Lair"           →  04.32_troll_lair.png
"05.32-Ilmaryen Keep"            →  05.32_ilmaryen_keep.png
"Ulgar Resticsard"               →  ulgar_resticsard.png
"Rothaar One-Leg"                →  rothaar_one-leg.png
"Grimbold"                       →  grimbold.png
```

### Image Output Locations

1. **thumbnail.png**: **Root directory of module** (NOT in images/ folder)
   - MUST be named exactly `thumbnail.png`
   - MUST be in module root, not images/ subdirectory
   - Recommended size: 800 pixels wide
2. **All other images**: `images/` subdirectory
   - `images/03.00_attercop_attack.png`
   - `images/ulgar_resticsard.png`
   - `images/05.32_ilmaryen_keep_cellars.png`

**Common Mistake:** Putting `cover.jpg` or `cover.png` in `images/` folder. This won't work! The thumbnail MUST be `thumbnail.png` in the root directory.

### Alternative: Manual Extraction

If `pdfimages` doesn't work well for your PDF:

1. Open PDF in a viewer
2. Take screenshots of maps and portraits
3. Crop to remove page elements
4. Save with appropriate names in images/ folder
5. Convert to PNG if needed

### Verification

After extraction and renaming:
```bash
# List all images to verify naming
ls -1 images/
ls -1 thumbnail.png

# Check that images match your stories/encounters
# Each image referenced in stories.yaml should exist
```

---

### Purpose
Extract maps, NPC portraits, and other illustrations from the PDF for use in the Fantasy Grounds module.

### General Rules

1. **First page (cover)**: Extract as `thumbnail.png` in module root directory
2. **Last page**: Skip entirely (usually product listing or ads)
3. **Second-to-last page**: Skip entirely (usually product listing or ads)
4. **Sections 1.0 and 2.0**: Skip all images from these sections
5. **Section 6.0 (Tables)**: Skip all images from the tables section
6. **Sections 3.0+**: Extract all maps and NPC portraits until reaching tables section

### Image Capture Guidelines

1. **Include image borders**: Capture decorative borders that are part of the image itself
2. **Exclude page borders**: Do not capture page numbers, headers, footers, or page margins
3. **When uncertain**: Err on the side of capturing the image with more context
4. **Clean crop**: Crop to the actual image content, but don't cut into the image itself

### Image Types to Extract

1. **Maps**:
   - Area overview maps (like "Mirkwood Area Map")
   - Terrain maps (like "Terrain Map: On the Trail of the Trolls")
   - Location maps (like "The Spiders' Lair")
   - Building floor plans (like "Ilmaryen Keep")
   - Tactical maps showing encounter areas

2. **NPC Portraits**:
   - Character illustrations (like portraits of Ulgar, Currael, Grimbold)
   - Creature illustrations (if shown separately from maps)

3. **Item Illustrations**:
   - Weapon illustrations
   - Magical item illustrations
   - Only if shown as separate detailed images

### Multi-Level Map Handling

When a single page contains multiple map levels (like floor plans of a multi-story building):

1. **Identify each distinct map** on the page
2. **Extract each map separately** as its own image file
3. **Name appropriately**:
   - `"05.32_ilmaryen_keep_cellars.png"`
   - `"05.32_ilmaryen_keep_first_level.png"`
   - `"05.32_ilmaryen_keep_second_level.png"`
   - `"05.32_ilmaryen_keep_tower_roofs.png"`

### Image Naming Convention

Convert the story/encounter name to snake_case:

1. **Start with story name**: `"CC.SS.AA-Name Here"`
2. **Convert to lowercase**: `"cc.ss.aa-name here"`
3. **Replace spaces with underscores**: `"cc.ss.aa-name_here"`
4. **Remove apostrophes**: `"gihellins_dagger"` not `"gihellin's_dagger"`
5. **Remove parentheses**: `"tumag_second"` not `"tumag_(second)"`
6. **Add .png extension**: `"cc.ss.aa-name_here.png"`

But keep the section number format with periods:
- `"03.34_spiders_lair.png"` (keep periods in section number)
- `"05.32.01_keep_entrance.png"` (keep periods in section and area numbers)

### Examples

```
Story/Encounter Name              →  Image Filename
"03.00-Attercop Attack"          →  03.00_attercop_attack.png
"03.34-The Spiders' Lair"        →  03.34_spiders_lair.png
"04.32-The Troll Lair"           →  04.32_troll_lair.png
"05.32-Ilmaryen Keep"            →  05.32_ilmaryen_keep.png
"Ulgar Resticsard"               →  ulgar_resticsard.png
"Rothaar One-Leg"                →  rothaar_one-leg.png
"Grimbold"                       →  grimbold.png
```

### Image Output Locations

1. **thumbnail.png**: **Root directory of module** (NOT in images/ folder)
   - MUST be named exactly `thumbnail.png`
   - MUST be in module root, not images/ subdirectory
   - Recommended size: 800 pixels wide
2. **All other images**: `images/` subdirectory
   - `images/03.00_attercop_attack.png`
   - `images/ulgar_resticsard.png`
   - `images/05.32_ilmaryen_keep_cellars.png`

**Common Mistake:** Putting `cover.jpg` or `cover.png` in `images/` folder. This won't work! The thumbnail MUST be `thumbnail.png` in the root directory.

### Page-by-Page Extraction for "Denizens of the Dark Wood"

Based on the PDF structure:

- **Page 1**: Extract as `thumbnail.png` (cover)
- **Pages 2-3**: Skip (section 1.0 - Guidelines)
- **Page 4**: Extract "Mirkwood Area Map" as `03.00_mirkwood_area.png`
- **Pages 5-11**: Process section 3.0 (Attercop Attack)
  - Extract NPC portraits (Ulgar, Currael)
  - Extract maps (terrain map, spiders' lair)
- **Pages 12-17**: Process section 4.0 (Trouble with Trolls)
  - Extract NPC portrait (Rothaar)
  - Extract maps (terrain map, troll lair)
- **Pages 18-27**: Process section 5.0 (The Tithing Train)
  - Extract NPC portrait (Grimbold)
  - Extract maps (terrain map, Ilmaryen Keep - multiple levels)
- **Pages 28-31**: Skip (section 6.0 - Tables)
- **Page 32**: Skip (second-to-last page)
- **Page 33**: Skip (last page)

### Image Association in YAML

After extracting images, reference them in stories.yaml:

```yaml
stories:
  - name: "03.34-The Spiders' Lair"
    text:
      - type: "header"
        content: "The Spiders' Lair"
      - type: "gm_notes"
        content: "The lair description..."
    images:
      - "03.34_spiders_lair.png"
```

---

## Validation Rules

### Cross-Reference Validation

1. **Items in npcs.yaml**: Every item listed in an NPC's items list must exist in items.yaml
2. **NPCs in encounters.yaml**: Every NPC listed in an encounter must exist in npcs.yaml
3. **NPCs in stories.yaml**: Every NPC listed in a story must exist in npcs.yaml
4. **Encounters in stories.yaml**: Every encounter listed in a story must exist in encounters.yaml
5. **Images in stories.yaml**: Every image listed in a story must exist as a file in images/

### Naming Validation

1. **Encounter names**: Must follow pattern `CC.SS.AA-Name` or `CC.SS-Name`
2. **Story names**: Must follow pattern `CC.SS.AA-Name` or `CC.SS-Name`
3. **Image names**: Must be derived from story/encounter names using snake_case rules
4. **NPC names**: Must be human-readable with proper capitalization
5. **Item names**: Must be human-readable with bonuses included

### Completeness Checks

1. **All named NPCs**: Every NPC with a name in sections 3.0+ must have an npcs.yaml entry
2. **All magic items**: Every magic item or special treasure must have an items.yaml entry
3. **All major encounters**: Significant combat or NPC meetings must have encounters.yaml entries
4. **All sections**: Major sections and areas must have stories.yaml entries
5. **All maps extracted**: Every map in sections 3.0+ must be extracted and named

---

## Summary Checklist

When processing a new PDF:

- [ ] Read sections 3.0+ (skip 1.0, 2.0, and tables section)
- [ ] Create items.yaml with all magic items and special treasures
- [ ] Create npcs.yaml with all named NPCs (use stats from tables section)
- [ ] Create encounters.yaml with specific encounter scenarios
- [ ] Create stories.yaml with narrative text (use proper text types)
- [ ] Extract thumbnail.png from page 1
- [ ] Extract all maps from sections 3.0+ to images/
- [ ] Extract all NPC portraits from sections 3.0+ to images/
- [ ] Name all images using snake_case derived from story names
- [ ] Validate all cross-references (items, NPCs, encounters, images)
- [ ] Create module.yaml LAST with correct metadata
  - **CRITICAL**: Set `output.directory: "./output"` (NOT `/mnt/user-data/outputs`)

---

## End of Instructions

These instructions provide a complete guide for extracting content from MERP adventure PDFs and creating properly structured YAML files for Fantasy Grounds module generation. Follow these instructions systematically, and ask questions when encountering ambiguous situations.
