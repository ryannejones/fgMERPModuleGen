# fgMERPModuleGen

`fgMERPModuleGen` generates **Fantasy Grounds MERP / RMC modules** (`.mod` files) from structured YAML input.
It assembles items, NPCs, and encounters into a module that can be imported directly into Fantasy Grounds.

This tool is designed to respect **canonical Fantasy Grounds / Arms Law data**. It does not invent rules, attack tables, or override ruleset behavior.

---

## Quickstart

```bash
python fg_generator.py /path/to/source
```

This will generate a `.mod` file in the `output/` directory use the yaml files in your source directory. 
You can use test_chapter6/ as an example. A clean set of templates will be furnished later. 

Copy the generated module into your Fantasy Grounds `modules/` directory and **restart Fantasy Grounds** before loading it.

> **Important:** Fantasy Grounds caches module data aggressively.  
> If changes do not appear, fully close and restart FG.
> If they still do not appear, right click on the module name in Modules and Reset. THIS WILL RESET EVERYTHING TO THE MODULE

---

## Inputs and Outputs

### Inputs
- `npcs.yaml` — custom NPC definitions
- `default_weapons.yaml` — default melee/missile weapons by NPC type
- Library data (e.g. `items_complete.json`) — canonical FG ruleset data

### Output
- `output/<module>.mod`
  - Contains `db.xml` with generated items, NPCs, and encounters

---

## Pipeline Overview

The generator runs in clearly defined phases (mirrored in console output):

### Phase 4: Generate Items XML
- Creates **module item definitions**
- These are the *master records* NPCs will reference
- Items are sourced from Fantasy Grounds library data

### Phase 5: Generate NPC XML
- Builds NPCs from YAML
- Resolves weapons using:
  - NPC-specific overrides
  - Defaults from `default_weapons.yaml`
- NPC weapons **reference module items** when possible

**Key rule:**  
NPCs do not define attack tables themselves — they inherit them from item definitions.

---

## Weapon Resolution Rules

Weapon assignment follows these rules:

1. If an NPC specifies a melee/missile weapon in `npcs.yaml`, it overrides defaults
2. Missing weapon types are filled from `default_weapons.yaml`
3. If a weapon exists as a module item:
   - The NPC weapon links to that item
   - The attack table is copied from the item definition
4. If a weapon is not generated as an item:
   - The NPC cannot link to it
   - No attack table can be inherited

---

## Attack Tables (Important)

Attack tables are **ruleset data**, not generator logic.

- Attack tables come from Fantasy Grounds / Arms Law content
- Multiple weapons may intentionally share the same attack table
- This tool preserves those mappings exactly

### Example (expected behavior)
- **Long Sword uses the Broadsword attack table (ALT-04)**  
  This is correct per Arms Law and should not be “fixed” in generator code.

If a weapon appears to have the “wrong” attack table:
1. Check the FG ruleset / Arms Law data first
2. Verify the item definition in the generated `db.xml`
3. Do **not** override ruleset behavior in the generator

Custom behavior requires **new items**, not overrides.

---

## Debugging and Verbosity

Use `-v` / `--verbose` to enable detailed debug output:

```bash
python fg_generator.py /path/to/source -v
```

This will print extensive internal state information useful for debugging.

If output is noisy, you probably ran with `-v`.

---

## Things This Tool Will Not Do

- It will not invent or modify attack tables
- It will not override Fantasy Grounds ruleset behavior
- It will not “correct” weapon-to-table mappings
- It will not support per-module ruleset customizations

If you need different behavior, create new items explicitly.

---

## Developer Notes

- Library data is treated as canonical
- Generated items are the single source of truth for NPC weapons
- Generator code should not compensate for or reinterpret ruleset data
- Debug output is gated behind the verbose flag

---

## Status

This project is under active development.  
Documentation is intentionally minimal and focused on correctness.
