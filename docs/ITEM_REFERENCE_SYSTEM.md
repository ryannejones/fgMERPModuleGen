# Item Reference System

## The Discovery

**Question**: When a player character loots an item from an NPC, does it create a reference or copy the data?

**Answer**: ✅ **Fantasy Grounds COPIES the data** (confirmed via FG forums and developer documentation)

## How It Works

### Within the Module
```xml
<!-- Item defined ONCE in module -->
<item>
  <id-00001>
    <name>Scimitar</name>
    <bonus type="number">0</bonus>
    <attacktable>
      <tableid>ALT-03</tableid>
    </attacktable>
    <!-- Complete item data -->
  </id-00001>
</item>

<!-- NPC references the item -->
<npc>
  <id-00001>
    <name>Orc Warrior</name>
    <weapons>
      <id-00001>
        <link type="windowreference">
          <class>item</class>
          <recordname>item.id-00001</recordname>
        </link>
      </id-00001>
    </weapons>
  </id-00001>
</npc>
```

### When Player Loots Item

**FG automatically:**
1. Detects item drag from NPC to character
2. Calls `DB.copyNode(sourceItem, characterInventory)`
3. **Copies complete item data** to character
4. Character now has self-contained item

**Result:**
- ✅ Character has full item data
- ✅ No reference to module
- ✅ Item works in any campaign
- ✅ Module can be unloaded

## Benefits

### 1. Single Point of Truth
```yaml
# Define item once
items:
  - name: "Scimitar"
    # ... complete data

# Multiple NPCs use it
npcs:
  - name: "Orc Warrior"
    # References Scimitar
  
  - name: "Orc Scout"  
    # Also references Scimitar
  
  - name: "Orc Leader"
    # Also references Scimitar
```

**Update once, changes everywhere** (until players loot)

### 2. Smaller Modules
- Scimitar data: ~2KB
- 50 Orcs with embedded scimitars: ~100KB
- 50 Orcs with references: ~50KB + 2KB = **52KB** (48% smaller!)

### 3. Character Portability
```
Campaign 1: Hildelith loots "Emerald Pendant of Strength"
           └─> FG copies full data to Hildelith
           
Export Hildelith to Campaign 2
           └─> Pendant data travels with character ✅
           
Campaign 2: Emerald Pendant works perfectly
           └─> No module needed!
```

### 4. Easy Updates
```yaml
# Before adventure starts:
items:
  - name: "Goblin Spear"
    bonus: 0  # Oops, too easy

# Test session reveals issue
# Update item definition:
items:
  - name: "Goblin Spear"
    bonus: -5  # Corrected

# All 20 goblins now have updated spears
# (Until players start looting them)
```

## How Looting Works

### Scenario: Player Defeats Orc

1. **GM opens NPC sheet**
   ```
   Orc Warrior
   └─ Weapons
      └─ Scimitar [link to item.id-00001]
   ```

2. **GM drags Scimitar to Hildelith**
   - FG detects drag operation
   - Source: `npc.id-00001.weapons.id-00001` (contains link)
   - FG resolves link → `item.id-00001`
   - FG copies ALL data from `item.id-00001`
   - FG creates new inventory entry in Hildelith

3. **Hildelith now has**
   ```xml
   <inventorylist>
     <id-00042>
       <name>Scimitar</name>
       <bonus type="number">0</bonus>
       <attacktable>
         <tableid>ALT-03</tableid>
       </attacktable>
       <!-- Complete copy, no reference! -->
     </id-00042>
   </inventorylist>
   ```

## What About Treasure Parcels?

Same system! Parcels reference module items:

```xml
<treasureparcels>
  <id-00001>
    <name>Goblin Hoard</name>
    <itemlist>
      <id-00001>
        <link type="windowreference">
          <class>item</class>
          <recordname>item.id-00005</recordname>
        </link>
        <count type="number">3</count>
      </id-00001>
    </itemlist>
  </id-00001>
</treasureparcels>
```

**When GM distributes parcel:**
- FG copies each item to character
- Characters get full data
- No references

## Edge Cases

### What if item NOT in module?

**NPC has custom weapon not in item list:**
```xml
<npc>
  <weapons>
    <id-00001>
      <!-- Embed full data directly -->
      <name>Skauril's Unique Sword +10</name>
      <bonus type="number">10</bonus>
      <!-- ... complete data -->
    </id-00001>
  </weapons>
</npc>
```

**Still works!** FG copies whatever data is there.

### What if player exports character, then reimports?

Character data is preserved. Items remain intact.

### What if GM loads old version of module?

Doesn't matter! Once items are looted, they're independent of module.

## YAML Workflow

### User creates module:

```yaml
# items.yaml - Master definitions
items:
  - name: "Broadsword"
  - name: "Scimitar"  
  - name: "Magic Sword +5"
    based_on: "Broadsword"
    modifications:
      bonus: 5

# npcs.yaml - NPCs reference items
npcs:
  - name: "Fighter"
    level: 5
    # Fighter in library has "Broadsword" in weapons
    # Generator creates reference to module item

  - name: "Orc Warrior"
    # Orc in library has "Scimitar" in weapons
    # Generator creates reference to module item

# parcels.yaml - Parcels reference items  
parcels:
  - name: "Treasure Chest"
    items:
      - name: "Magic Sword +5"
        count: 1
      - name: "Broadsword"
        count: 3
    # Generator creates references to module items
```

### Generator creates:

```xml
<module>
  <!-- Item definitions (once each) -->
  <item>
    <id-00001><name>Broadsword</name>...</id-00001>
    <id-00002><name>Scimitar</name>...</id-00002>
    <id-00003><name>Magic Sword +5</name>...</id-00003>
  </item>
  
  <!-- NPCs (reference items) -->
  <npc>
    <id-00001>
      <name>Fighter</name>
      <weapons>
        <id-00001>
          <link>item.id-00001</link> <!-- Broadsword -->
        </id-00001>
      </weapons>
    </id-00001>
    
    <id-00002>
      <name>Orc Warrior</name>
      <weapons>
        <id-00001>
          <link>item.id-00002</link> <!-- Scimitar -->
        </id-00001>
      </weapons>
    </id-00002>
  </npc>
  
  <!-- Parcels (reference items) -->
  <treasureparcels>
    <id-00001>
      <name>Treasure Chest</name>
      <itemlist>
        <id-00001>
          <link>item.id-00003</link> <!-- Magic Sword +5 -->
          <count>1</count>
        </id-00001>
        <id-00002>
          <link>item.id-00001</link> <!-- Broadsword -->
          <count>3</count>
        </id-00002>
      </itemlist>
    </id-00001>
  </treasureparcels>
</module>
```

## Sources

Research conducted via Fantasy Grounds forums:

1. **DB.copyNode behavior** - Confirmed that when items are dragged to character inventory, "a copy of the record is created"

2. **Module items** - Items in modules are complete definitions, not just references

3. **Character portability** - Characters exported with inventory maintain full item data

## Implementation Status

✅ **v0.11**: db_npcs.py and db_items.py updated to use reference system
- Items generated with complete data once
- NPCs reference module items  
- Parcels reference module items
- FG handles copying on loot/distribution

## Best Practices

### For Module Creators

1. **Define all common items in items.yaml**
   ```yaml
   items:
     - name: "Broadsword"
     - name: "Scimitar"
     - name: "Longbow"
   ```

2. **NPCs automatically reference them**
   - If NPC from library has "Broadsword", generator creates reference
   - No manual work needed

3. **Custom items in item list too**
   ```yaml
   items:
     - name: "Skauril's Flaming Sword"
       based_on: "Broadsword"
       modifications:
         bonus: 10
   ```

4. **Truly unique items can be embedded**
   - If item not in items.yaml
   - Generator embeds full data in NPC
   - Still lootable

### For GMs

1. **Module must be loaded during play**
   - References resolve during session
   - Once looted, no longer needed

2. **Players can export characters anytime**
   - Looted items travel with character
   - Work in any campaign

3. **Update items before session**
   - Changes affect all NPCs
   - Until items are looted

## Summary

🎉 **Best of all worlds:**

✅ Module has single point of truth (easy updates)
✅ Module files are smaller (references not copies)
✅ Characters are portable (FG copies on loot)
✅ No broken references (copies are complete)
✅ Works exactly as GMs expect

**This is the way.**
