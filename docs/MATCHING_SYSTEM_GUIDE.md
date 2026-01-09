# Entity Matching System Documentation

## Overview

The matching system resolves user-provided names (from YAML files) to actual library entries using multiple strategies with intelligent fallbacks.

## Default Level: 5 (UPDATED)

**When level not specified, default is 5 (not 4)**

**Reasoning:**
- Character Law templates exist at: 1, 3, 5, 7, 10, 15, 20
- Level 4 doesn't exist, so we use 5 (closest to mid-range)
- Most "Ready Adventures" target levels 4-6, and level 5 fits perfectly
- Level 5 represents competent but not exceptional NPCs

**If user specifies a level that doesn't exist:**
- Round to nearest available level
- Warn user about the rounding

Available levels: **1, 3, 5, 7, 10, 15, 20**

## Matching Strategies

The system tries strategies in order until one succeeds:

### 1. Exact Match
Tries to find exact name in library (case-insensitive)

```yaml
npcs:
  - name: "Wolf"  # Exact match in library
```

### 2. Profession Mapping
Maps profession names to NPC templates

```yaml
npcs:
  - name: "Animist"
    level: 10
    # Maps to "Pure Channeling Spell User Level 10"
```

**Profession Mappings:**
- Animist, Cleric → Pure Channeling Spell User
- Mage, Illusionist, Alchemist → Pure Essence Spell User
- Mystic, Lay Healer, Healer, Mentalist → Pure Mentalism Spell User
- Warrior, Soldier, Guard, Knight, Mercenary → Fighter
- Bandit, Burglar, Assassin, Spy → Rogue
- Scout, Tracker, Woodsman, Hunter → Ranger

### 3. Creature Aliases
Maps common creature name variations

```yaml
npcs:
  - name: "Warg"  # Maps to "Wolf"
```

**Creature Aliases:**
- Warg, Dire Wolf, War Dog → Wolf
- Orc → Orc (non-combatant)
- Uruk → Orc (leader)
- Troll, Cave Troll → Troll
- Spider, Giant Spider, Great Spider → Spider, Large

### 4. Generic Terms
Maps generic descriptors to templates

```yaml
npcs:
  - name: "Scout"  # Maps to "Ranger" template, uses default level 5
```

### 5. Fuzzy Matching
If no exact match, tries fuzzy matching (80%+ similarity)

```yaml
npcs:
  - name: "Wolfe"  # Typo - fuzzy matches to "Wolf" at 92% similarity
```

**Fuzzy Match Examples:**
- "Brodsword" → "Broadsword" ✓
- "Wolfs" → "Wolf" ✓
- "Rangr" → "Ranger" ✓
- "Bird" → "Broadsword" ✗ (too different)

**High confidence (90%+):** Automatically used
**Lower confidence (80-90%):** Provided as suggestions, user must confirm

### 6. Graceful Failure
If nothing matches, provides suggestions

```
NPC 'Dragon' not found
Suggestions:
  - Dragonskin Armor
  - Dragonfly
```

## Usage Examples

### Example 1: Standard Creatures
```yaml
encounters:
  - name: "Forest Encounter"
    npcs:
      - name: "Wolf"        # Exact match
        count: 3
      
      - name: "Warg"        # Alias → Wolf
        count: 2
```

### Example 2: Profession-Based NPCs
```yaml
npcs:
  - name: "Animist"         # Profession mapping
    level: 10               # Explicit level
    
  - name: "Scout"           # Generic → Ranger
                            # Uses default level 5
    
  - name: "Warrior"         # Generic → Fighter
    level: 7                # Explicit level
```

### Example 3: Named NPCs (Custom)
```yaml
npcs:
  - name: "Skauril"
    based_on: "Warrior"     # Mapped to Fighter
    level: 15
    modifications:
      hits:
        "@type": "number"
        "_text": "150"
      db:
        "@type": "number"
        "_text": "75"
```

### Example 4: Items
```yaml
items:
  - name: "Broadsword"      # Exact match
    count: 5
    
  - name: "Sword"           # Alias → Broadsword
    count: 3
    
  - name: "Magic Sword +5"
    based_on: "Sword"       # Alias → Broadsword
    modifications:
      bonus:
        "@type": "number"
        "_text": "5"
```

## Level Handling

### NPCs/Creatures Without Levels
Fixed-stat creatures (Wolf, Orc, Troll) use their standard stats:
```yaml
npcs:
  - name: "Wolf"  # No level needed, uses standard Wolf stats
```

### NPCs With Levels
Profession-based NPCs REQUIRE levels (or use default 5):
```yaml
npcs:
  - name: "Fighter"
    level: 10     # Explicit
    
  - name: "Ranger"  # Uses default level 5
```

### Custom NPCs
Always specify level for the base template:
```yaml
npcs:
  - name: "Elite Guard"
    based_on: "Fighter"
    level: 12  # Rounds to nearest: 10
```

## Level Rounding

If user specifies unavailable level, round to nearest:

| Requested | Rounded To | Reason |
|-----------|------------|--------|
| 2 | 3 | Closer to 3 than 1 |
| 4 | 5 | Closer to 5 than 3 |
| 6 | 5 | Closer to 5 than 7 |
| 8 | 7 | Closer to 7 than 10 |
| 11 | 10 | Closer to 10 than 15 |
| 13 | 15 | Closer to 15 than 10 |
| 18 | 20 | Closer to 20 than 15 |

## Error Handling

### Not Found - No Suggestions
```
Error: NPC 'Unicorn' not found
No similar entries found.
Please check spelling or consult library.
```

### Not Found - With Suggestions
```
Error: NPC 'Wolff' not found
Did you mean:
  - Wolf (95% match)
  - Wolverine (67% match)
```

### Ambiguous Match
```
Warning: 'Orc' has multiple variants
Using: Orc (non-combatant)
Other options: Orc (leader), Orc (commander)
```

## API Usage

```python
from entity_matcher import EntityMatcher
from npc_creature_library_complete import CompleteNPCCreatureLibrary
from item_library_complete import CompleteItemLibrary

# Initialize
npc_lib = CompleteNPCCreatureLibrary()
item_lib = CompleteItemLibrary()
matcher = EntityMatcher(npc_lib, item_lib)

# Match NPC
result = matcher.match_npc("Animist", level=10)
if result['found']:
    npc_entry = result['entry']
    print(f"Matched: {result['matched_name']}")
    print(f"Method: {result['method']}")

# Create custom NPC
result = matcher.create_custom_npc(
    name="Skauril",
    based_on="Warrior",
    level=15,
    modifications={"hits": {"@type": "number", "_text": "150"}}
)

if result['success']:
    custom_npc = result['entry']
```

## Files

- `npc_creature_item_mappings.yaml` - Mapping definitions
- `entity_matcher.py` - Matching system implementation
- `npc_creature_library_complete.py` - NPC/creature library
- `item_library_complete.py` - Item library

## Maintenance

### Adding New Mappings

Edit `npc_creature_item_mappings.yaml`:

```yaml
professions:
  # Add new profession mapping
  Druid: "Pure Channeling Spell User"

creatures:
  # Add new creature alias
  "Dire Bear": "Bear"
```

### Adjusting Fuzzy Threshold

Edit `entity_matcher.py`:

```python
class EntityMatcher:
    FUZZY_THRESHOLD = 0.80  # Adjust this (0.0-1.0)
```

Lower = more lenient (more false positives)
Higher = stricter (fewer matches)

## Summary

The matching system provides:
- ✅ Exact matching for precise requests
- ✅ Intelligent profession and alias mappings
- ✅ Fuzzy matching for typos
- ✅ Graceful failure with suggestions
- ✅ Default level 5 for profession-based NPCs
- ✅ Level rounding to nearest available

Users write simple YAML, system handles the complexity!
