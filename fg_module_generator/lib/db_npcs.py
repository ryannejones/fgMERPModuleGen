"""
NPC XML Generator - Generate <npc> section from npcs.yaml
"""

import xml.etree.ElementTree as ET

class NPCGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.next_id = 1
        self.weapon_next_id = 1
    
    def get_next_id(self):
        """Get next NPC ID"""
        npc_id = f"id-{self.next_id:05d}"
        self.next_id += 1
        return npc_id
    
    def get_next_weapon_id(self):
        """Get next weapon ID"""
        weapon_id = f"id-{self.weapon_next_id:05d}"
        self.weapon_next_id += 1
        return weapon_id
    
    def get_attack_table(self, weapon_name):
        """Get attack table for a weapon"""
        weapon_data = self.library.get_weapon(weapon_name)
        if weapon_data:
            return weapon_data.get('table', 'ALT-01')  # Default to ALT-01 if not found
        return 'ALT-01'  # Default
    
    def create_weapon_element(self, weapon, parent):
        """Create a weapon element"""
        weapon_id = self.get_next_weapon_id()
        weapon_elem = ET.SubElement(parent, weapon_id)
        
        # Weapon name
        name = ET.SubElement(weapon_elem, 'name')
        name.set('type', 'string')
        name.text = weapon.get('weapon', 'Unknown Weapon')
        
        # Offensive Bonus
        ob = ET.SubElement(weapon_elem, 'ob')
        ob.set('type', 'number')
        ob.text = str(weapon.get('ob', 0))
        
        # Attack table
        attacktable = ET.SubElement(weapon_elem, 'attacktable')
        
        # Check if custom attack table provided
        if 'attack_table' in weapon:
            table_id = weapon['attack_table']
        else:
            # Look up from Arms Law
            weapon_name = weapon.get('weapon')
            table_id = self.get_attack_table(weapon_name)
        
        tableid = ET.SubElement(attacktable, 'tableid')
        tableid.set('type', 'string')
        tableid.text = table_id
        
        # Bonus (magical bonus)
        if 'bonus' in weapon:
            bonus = ET.SubElement(weapon_elem, 'bonus')
            bonus.set('type', 'number')
            bonus.text = str(weapon['bonus'])
        
        return weapon_elem
    
    def create_defence_element(self, defence, parent):
        """Create a defence element"""
        defence_id = self.get_next_weapon_id()  # Reuse weapon ID counter
        defence_elem = ET.SubElement(parent, defence_id)
        
        # Defence name
        name = ET.SubElement(defence_elem, 'name')
        name.set('type', 'string')
        name.text = defence.get('name', 'Shield')
        
        # Melee bonus
        if 'melee_bonus' in defence:
            melee = ET.SubElement(defence_elem, 'meleedefense')
            melee.set('type', 'number')
            melee.text = str(defence['melee_bonus'])
        
        # Missile bonus
        if 'missile_bonus' in defence:
            missile = ET.SubElement(defence_elem, 'missiledefense')
            missile.set('type', 'number')
            missile.text = str(defence['missile_bonus'])
        
        return defence_elem
    
    def create_npc(self, npc):
        """Create an NPC element"""
        npc_id = self.get_next_id()
        npc_elem = ET.Element(npc_id)
        
        # Store ID for cross-referencing
        npc['_id'] = npc_id
        self.loader.name_to_id['npc'][npc['name']] = npc_id
        
        # Name
        name = ET.SubElement(npc_elem, 'name')
        name.set('type', 'string')
        name.text = npc['name']
        
        # Level
        level = ET.SubElement(npc_elem, 'level')
        level.set('type', 'number')
        level.text = str(npc.get('level', 1))
        
        # Hit Points
        hits = ET.SubElement(npc_elem, 'hits')
        hits.set('type', 'number')
        hits.text = str(npc.get('hp', 10))
        
        # Armor Type
        armortype = ET.SubElement(npc_elem, 'armortype')
        armortype.set('type', 'number')
        armortype.text = str(npc.get('at', 1))
        
        # Defensive Bonus
        db = ET.SubElement(npc_elem, 'defensivebonus')
        db.set('type', 'number')
        db.text = str(npc.get('db', 0))
        
        # Base Rate (movement)
        if 'baserate' in npc:
            baserate = ET.SubElement(npc_elem, 'baserate')
            baserate.set('type', 'number')
            baserate.text = str(npc['baserate'])
        
        # Profession
        if 'profession' in npc:
            profession = ET.SubElement(npc_elem, 'profession')
            profession.set('type', 'string')
            profession.text = npc['profession']
        
        # Group (NPCs vs Monsters)
        if 'group' in npc:
            group = ET.SubElement(npc_elem, 'type')
            group.set('type', 'string')
            group.text = npc['group']
        
        # Weapons
        if 'weapons' in npc and npc['weapons']:
            weapons = ET.SubElement(npc_elem, 'weapons')
            for weapon in npc['weapons']:
                self.create_weapon_element(weapon, weapons)
        
        # Defences
        if 'defences' in npc and npc['defences']:
            defences = ET.SubElement(npc_elem, 'defences')
            for defence in npc['defences']:
                self.create_defence_element(defence, defences)
        
        # Abilities (special abilities text)
        if 'abilities' in npc:
            abilities = ET.SubElement(npc_elem, 'abilities')
            abilities.set('type', 'formattedtext')
            p = ET.SubElement(abilities, 'p')
            p.text = npc['abilities']
        
        # Spells
        if 'spells' in npc:
            spells = ET.SubElement(npc_elem, 'spells')
            spells.set('type', 'formattedtext')
            p = ET.SubElement(spells, 'p')
            p.text = npc['spells']
        
        # Description
        if 'description' in npc:
            description = ET.SubElement(npc_elem, 'description')
            description.set('type', 'formattedtext')
            p = ET.SubElement(description, 'p')
            p.text = npc['description']
        
        return npc_elem
    
    def generate(self):
        """Generate the complete <npc> section"""
        if not self.loader.npcs:
            return None
        
        if self.verbose:
            print(f"  Generating {len(self.loader.npcs)} custom NPCs...")
        
        # Create root npc element
        npc_root = ET.Element('npc')
        
        for npc in self.loader.npcs:
            npc_elem = self.create_npc(npc)
            npc_root.append(npc_elem)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.npcs)} custom NPCs")
        
        return npc_root
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
