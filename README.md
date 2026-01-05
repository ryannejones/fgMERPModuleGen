# fgMERPModuleGen
Fantasy Grounds MERP Module Generator
============================================================

A generator to create and add to Fantasty Grounds MERP modules using user provided yaml files for
* Stories
* Items (includes weapons and armor)
* NPCs
* Encounters
* Parcels
* Images (requires folder called images/ in directory yaml files are in)

Prerequisites: 
python 3.9.6 (and probably higher)
PyYaml 
Fantasy Grounds Modules 
    MERP Character Law
    MERP Arms Law
    MERP Spell Law
    MERP Creatures and Treasures

## This generator is incomplete. It can currently create battle/encounter XML and validate yaml files. 

## Usage

Validate yaml files 
```bash
python3 fg_generator.py ../test_chapter6/ --validate-only
```

Create XML files for module
```bash
python3 fg_generator.py ../test_chapter6/
```


## Code Structure

**lib/db_battles.py**
- `BattleGenerator` class
- `create_npc_list_entry()` - Creates NPC references
- `create_battle()` - Creates complete battle entry
- `generate()` - Generates entire <battle> section
- `to_xml_string()` - Formats XML for output


## Phase 4: Battle XML Generation

Phase 4 is now complete! The generator can now create proper Fantasy Grounds battle XML from encounters.yaml.

## What Phase 4 Does

Converts this YAML:

```yaml
encounters:
  - name: "6.5.02 - Bridge Crew"
    exp: 800
    npcs:
      - creature: "Ranger Level 5"
        count: 1
        faction: foe
        display_name: "Bridge Crew Ranger"
```

Into this XML:

```xml
<battle>
  <id-00007>
    <exp type="number">800</exp>
    <name type="string">6.5.02 - Bridge Crew</name>
    <npclist>
      <id-00019>
        <count type="number">1</count>
        <faction type="string">foe</faction>
        <link type="windowreference">
          <class>npc</class>
          <recordname>reference.npcs.rangerlevel5@Character Law</recordname>
        </link>
        <name type="string">Bridge Crew Ranger</name>
      </id-00019>
    </npclist>
  </id-00007>
</battle>
```

## Features

- [DONE] Auto-assigns sequential IDs
- [DONE] Links to library creatures automatically
- [DONE] Supports display names for NPCs
- [DONE] Handles factions (foe/friend/neutral)
- [DONE] Supports multiple NPCs per encounter
- [DONE] Experience point calculation
- [DONE] Proper XML structure for Fantasy Grounds


## Next Phases

Still needed:

- [TODO] Phase 5: Story XML generation
- [TODO] Phase 6: NPC XML generation
- [TODO] Phase 7: Items/Parcels XML
- [TODO] Phase 8: Images XML
- [TODO] Phase 9: DB.xml assembly
- [TODO] Phase 10: Module packaging
- [TODO] Phase 11: Update mode
- [TODO] Misc: Update README - include how to format yaml files, how to know if custom npc or item is needed
- [TODO] Templates: Provide empty yaml templates

