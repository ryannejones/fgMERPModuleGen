# Skills Reference System

## How Skills Work

Skills in NPCs are **already properly referenced** to Character Law. No additional work needed!

## Structure

Each skill in an NPC contains:
1. **Reference to Character Law** (`open` field) - Links to skill definition
2. **NPC-specific values**:
   - `bonus`: Total skill bonus for this NPC
   - `ranks`: Number of ranks this NPC has in the skill

## Example Skill Data in NPC

```json
{
  "skills": {
    "id-00001": {
      "name": {
        "@type": "string",
        "_text": "Climb"
      },
      "open": {
        "@type": "windowreference",
        "class": { "_text": "skill" },
        "recordname": {
          "_text": "reference.skilllist.primaryskills.list.id-00011@Character Law"
        }
      },
      "bonus": {
        "@type": "number",
        "_text": "20"
      },
      "ranks": {
        "@type": "number",
        "_text": "0"
      }
    }
  }
}
```

## What Gets Copied

When copying an NPC (standard or custom):
- ✅ **Keep the skill references** - These point to Character Law definitions
- ✅ **Keep/modify bonus and ranks** - These are NPC-specific values
- ❌ **Don't copy skill definitions** - Already in Character Law module

## Skill Reference Table

The `skill_references.json` file contains 80 skills mapped to their Character Law references:

```json
{
  "skills": {
    "climb": {
      "name": "Climb",
      "id": "id-00011",
      "category": "primaryskills",
      "reference_path": "reference.skilllist.primaryskills.list.id-00011@Character Law"
    },
    "ambush": {
      "name": "Ambush",
      "id": "id-00023",
      "category": "primaryskills",
      "reference_path": "reference.skilllist.primaryskills.list.id-00023@Character Law"
    }
    // ... 78 more skills
  }
}
```

## Skill Categories

Skills are organized in Character Law:
1. **Primary Skills** (most common)
2. **Secondary Skills**
3. **Unskilled Actions**

## Module Generation

When generating Fantasy Grounds modules:

### For Standard NPCs (from library)
```xml
<npc>
  <id-00001>
    <name type="string">Fighter Level 05</name>
    <skills>
      <id-00001>
        <name type="string">Climb</name>
        <open type="windowreference">
          <class>skill</class>
          <recordname>reference.skilllist.primaryskills.list.id-00011@Character Law</recordname>
        </open>
        <bonus type="number">20</bonus>
        <ranks type="number">0</ranks>
      </id-00001>
      <!-- more skills -->
    </skills>
  </id-00001>
</npc>
```

The `open` reference links to Character Law, which must be loaded as a prerequisite module.

### For Custom NPCs
Same structure - keep the skill references from the base NPC, modify bonuses/ranks as needed:

```yaml
npcs:
  - name: "Elite Scout"
    based_on: "Ranger"
    level: 10
    modifications:
      # Can modify individual skill bonuses
      skills:
        id-00001:  # Climb skill
          bonus: 
            "@type": "number"
            "_text": "50"  # Increased from base
```

## Why This Works

1. **References not copies**: Skills link to Character Law, don't duplicate data
2. **Module dependency**: Users must have Character Law loaded (it's a prerequisite)
3. **Customizable**: Each NPC has its own bonus/ranks values
4. **No fuzzy matching needed**: Skill names are standardized in Character Law
5. **Already complete**: The skill references in extracted NPCs are correct as-is

## No Additional Work Required

✅ Skill references already in NPC data
✅ Skill reference table extracted for documentation
✅ No separate skill library needed
✅ No skill matching system needed
✅ Just copy skills as-is when creating NPCs

## Summary

**Skills are already handled correctly in the system.**

When you copy an NPC:
- The skills array comes with it
- References to Character Law are preserved
- Bonus/ranks values are copied (and can be modified)
- Users must have Character Law module (prerequisite)

**No action needed for skills!**
