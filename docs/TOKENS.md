# Token Support

The Fantasy Grounds module generator automatically detects and assigns token images to NPCs. Tokens are the visual representations of NPCs that appear in the combat tracker and on maps.

## Token Assignment Methods

There are **two ways** to assign tokens to NPCs:

1. **YAML Token References** - Reference tokens from FG modules or external sources
2. **File-Based Tokens** - Provide your own token image files

The generator checks in this priority order:
1. YAML tokens specified in `npcs.yaml` (if provided)
2. Token files in `tokens/` folder (auto-detected by name)
3. No tokens → Fantasy Grounds generates letter badges automatically

## Method 1: YAML Token References

Specify token references directly in your `npcs.yaml` file. This is useful for referencing tokens from Fantasy Grounds' built-in token packs or other loaded modules.

### YAML Format

```yaml
npcs:
  - name: "Gihellin"
    race: "Elf"
    profession: "Mage"
    level: 5
    tokens:
      picture: "tokens/elf_male_noble_a_01.png@Character Pogs"
      token: "tokens/elf_male_adventurer_a_01.png@Character Tokens"
      token3dflat: "tokens/elf_warrior_topdown.png@Top Down Tokens"
```

### Token Reference Format

The format for referencing external tokens is:

```
tokens/{filename}@{module_name}
```

**Examples:**
- `tokens/elf_male_noble_a_01.png@Character Pogs`
- `tokens/dwarf_warrior.png@Character Tokens`
- `tokens/orc_topdown.png@Top Down Tokens`

### Available Token Types in YAML

You can specify any combination of these three token types:

- **`picture`** - Portrait/artwork of the NPC
- **`token`** - Standard token (front-facing view)
- **`token3dflat`** - Top-down token view

All three are optional. You can specify just one, two, or all three.

### YAML Token Examples

**Example 1: Reference all three token types from FG modules**
```yaml
npcs:
  - name: "Elven Ranger"
    profession: "Ranger"
    level: 10
    tokens:
      picture: "tokens/elf_ranger_portrait.png@Character Pogs"
      token: "tokens/elf_ranger.png@Character Tokens"
      token3dflat: "tokens/elf_ranger_top.png@Top Down Tokens"
```

**Example 2: Only specify picture**
```yaml
npcs:
  - name: "Human Fighter"
    profession: "Fighter"
    level: 5
    tokens:
      picture: "tokens/human_fighter.png@Character Pogs"
```

**Example 3: Mix of different modules**
```yaml
npcs:
  - name: "Orc Chieftain"
    based_on: "Orc, Greater"
    level: 8
    tokens:
      token: "tokens/orc_leader.png@Monster Tokens"
      token3dflat: "tokens/orc_chief_top.png@Top Down Tokens"
```

## Method 2: File-Based Tokens

Place token image files in the `tokens/` folder within your adventure directory. The generator will automatically detect and assign them based on NPC names.

## Token Types

Fantasy Grounds supports three types of tokens for each NPC:

1. **Picture** - Portrait/artwork of the NPC (displayed in character sheets and some UI elements)
2. **Token** - Standard token image (displayed in combat tracker)
3. **Token 3D Flat** - Top-down token view (used on maps, looking down from above)

You can provide any combination of these three types. If no tokens are provided, Fantasy Grounds will automatically generate letter badges (like "B", "W", "S").

## Token File Naming Convention

Token files must follow this naming pattern:

```
{type}-{normalized_name}.{extension}
```

Where:
- **{type}** is one of: `picture`, `token`, or `token3dflat`
- **{normalized_name}** is the NPC name after normalization (see below)
- **{extension}** is an image format: `.png`, `.jpg`, `.jpeg`, or `.webp`

### Name Normalization Rules

NPC names are normalized using these rules:

1. Convert to lowercase
2. Replace spaces with underscores
3. Remove parentheses and their contents (extracting what's inside)
4. Strip "Level X" and "(Xth Level)" suffixes
5. Remove special characters

**Examples:**

| NPC Name | Normalized Name | Token Filename |
|----------|----------------|----------------|
| Gihellin | gihellin | `picture-gihellin.png` |
| Orc Scout | orc_scout | `token-orc_scout.png` |
| Orc (leader) | orc_leader | `picture-orc_leader.png` |
| Ranger Level 15 | ranger | `token-ranger.png` |
| Scout (3rd Level) | scout | `token3dflat-scout.png` |
| Fighter Level 03 | fighter | `picture-fighter.png` |

## Directory Structure

Place all token images in the `tokens/` folder within your adventure directory:

```
test_chapter6/
  tokens/
    picture-gihellin.png
    token-gihellin.png
    token3dflat-gihellin.png
    
    picture-orc_scout.png
    token-orc_scout.png
    
    picture-orc_leader.png
    token-orc_leader.png
    token3dflat-orc_leader.png
    
    picture-ranger.png
    token-ranger.png
    
    picture-scout.png
```

## Token Image Guidelines

### Recommended Specifications

- **Format**: PNG (for transparency) or JPG
- **Size**: 
  - Picture: 200x200 to 400x400 pixels
  - Token: 100x100 to 200x200 pixels (usually circular or with rounded corners)
  - Token 3D Flat: 70x70 to 140x140 pixels (top-down view)
- **Background**: Transparent (PNG) or solid color
- **Style**: Consistent across your module

### Token Design Tips

1. **Pictures** - Use portrait-style artwork showing the character's face and upper body
2. **Tokens** - Design as if looking at the character at eye level (front view)
3. **Token 3D Flat** - Design as if looking down from directly above (bird's eye view)

## How It Works

1. **Detection**: The generator scans the `tokens/` folder for all image files
2. **Matching**: For each NPC, it normalizes the name and looks for matching token files
3. **Assignment**: If tokens are found, it adds the appropriate XML tags to the NPC
4. **Packaging**: All token files are copied into the module's `tokens/` folder

## Usage Examples

### Example 1: Named NPC with All Three Tokens

For a named NPC called "Gihellin":

```
tokens/
  picture-gihellin.png          ← Portrait artwork
  token-gihellin.png            ← Front-facing token
  token3dflat-gihellin.png      ← Top-down token
```

### Example 2: Generic NPC Type with Partial Tokens

For "Scout (3rd Level)" NPCs (all levels share the same tokens):

```
tokens/
  picture-scout.png             ← Picture only
  token-scout.png               ← Standard token only
```

### Example 3: Creature with Special Characters

For "Orc (leader)":

```
tokens/
  picture-orc_leader.png        ← Note: parentheses removed
  token-orc_leader.png
  token3dflat-orc_leader.png
```

### Example 4: Multiple NPC Types

```
tokens/
  picture-gihellin.png
  token-gihellin.png
  
  picture-orc_scout.png
  token-orc_scout.png
  token3dflat-orc_scout.png
  
  picture-orc_leader.png
  token-orc_leader.png
  
  picture-ranger.png
  token-ranger.png
  
  picture-animist.png
  token-animist.png
```

## Troubleshooting

### Tokens Not Appearing

1. **Check filename format**: Ensure you're using the correct pattern: `{type}-{normalized_name}.{ext}`
2. **Check name normalization**: Run your NPC name through the normalization rules
3. **Check file extension**: Only `.png`, `.jpg`, `.jpeg`, and `.webp` are supported
4. **Check verbose output**: Run with `-v` flag to see token detection messages

### Wrong Token Assigned

- Verify the normalized name matches what the generator expects
- Check for multiple files with similar names
- Use verbose mode to see what tokens are detected and matched

### Token Shows as Letter Badge

This is normal behavior when no token file is provided. Fantasy Grounds will automatically generate letter badges (B, W, S, etc.) for NPCs without tokens.

## Advanced Usage

### Sharing Tokens Across NPC Levels

Generic NPCs like "Fighter Level 03" and "Fighter Level 15" will both use tokens named `picture-fighter.png` since the level suffix is stripped during normalization.

This is intentional - it allows you to provide one set of tokens for all levels of the same NPC type.

### Custom vs Generic NPCs

- **Named NPCs** (like "Gihellin", "Gardagd") should have unique tokens
- **Generic NPCs** (like "Scout", "Ranger", "Fighter") can share tokens across levels
- **Creatures** (like "Orc Scout", "Orc (leader)") should have type-specific tokens

## XML Structure

For reference, the generator adds these XML tags when tokens are found:

```xml
<picture type="token">tokens/picture-gihellin.png</picture>
<token type="token">tokens/token-gihellin.png</token>
<token3Dflat type="token">tokens/token3dflat-gihellin.png</token3Dflat>
```

These reference the files in the module's `tokens/` folder using relative paths.
