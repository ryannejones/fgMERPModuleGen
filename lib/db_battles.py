"""
Battle XML Generator - Generate <battle> section from encounters
"""

import xml.etree.ElementTree as ET

class BattleGenerator:
    def __init__(self, loader, library, verbose=False):
        self.loader = loader
        self.library = library
        self.verbose = verbose
        self.next_id = 1
        self.npc_next_id = 1
    
    def get_next_id(self):
        """Get next battle ID"""
        battle_id = f"id-{self.next_id:05d}"
        self.next_id += 1
        return battle_id
    
    def get_next_npc_id(self):
        """Get next NPC list entry ID"""
        npc_id = f"id-{self.npc_next_id:05d}"
        self.npc_next_id += 1
        return npc_id
    
    def get_creature_link(self, creature_name):
        """Get the link reference for a creature"""
        mod = self.loader.config["name"]
        # Check if it's a custom NPC from npcs.yaml
        if creature_name in self.loader.name_to_id.get('npc', {}):
            npc_id = self.loader.name_to_id['npc'][creature_name]
            return {
                'class': 'npc',
                'recordname': f'npc.{npc_id}'
            }
        
        # All other NPCs will be generated into the module by NPCGenerator
        # Use a placeholder - the actual ID will be assigned during generation
        # For now, create a predictable ID based on name
        safe_name = creature_name.lower().replace(" ", "").replace("'", "")
        return {
            'class': 'npc',
            'recordname': f'npc.{safe_name}'
        }
    
    def create_npc_list_entry(self, npc_ref, parent):
        """Create an NPC list entry element"""
        entry_id = self.get_next_npc_id()
        entry = ET.SubElement(parent, entry_id)
        
        # Count
        count = ET.SubElement(entry, 'count')
        count.set('type', 'number')
        count.text = str(npc_ref.get('count', 1))
        
        # Faction (foe, friend, neutral)
        faction = ET.SubElement(entry, 'faction')
        faction.set('type', 'string')
        faction.text = npc_ref.get('faction', 'foe')
        
        # Link to creature
        link = ET.SubElement(entry, 'link')
        link.set('type', 'windowreference')
        
        # Support both 'creature' (old) and 'name' (new)
        creature_name = npc_ref.get('creature') or npc_ref.get('name')
        
        # If display_name is provided, link to that NPC instead (it should exist as a variant)
        # Otherwise link to the base creature
        link_name = npc_ref.get('display_name') or creature_name
        link_data = self.get_creature_link(link_name)
        
        link_class = ET.SubElement(link, 'class')
        link_class.text = link_data['class']
        
        recordname = ET.SubElement(link, 'recordname')
        recordname.text = link_data['recordname']
        
        # Name (use display_name if provided, otherwise creature name)
        name = ET.SubElement(entry, 'name')
        name.set('type', 'string')
        name.text = link_name
        
        # Token (encounter-row token drives placement icon in encounter list)
        token_value = npc_ref.get("token")

        if not token_value:
            # recordname looks like: npc.id-00020@skaurilsarmy
            rn = link_data.get("recordname", "")
            if rn.startswith("npc.") and "@".join(rn.split("@")[1:]):
                base, mod = rn.split("@", 1)          # base = npc.id-00020
                npc_id = base.replace("npc.", "")     # id-00020
                token_value = f"tokens/{npc_id}.png"
            elif rn.startswith("npc."):
                base = rn.split("@", 1)[0]
                npc_id = base.replace("npc.", "")
                mod = self.loader.config["name"]
                token_value = f"tokens/{npc_id}.png"

        if token_value:
            token = ET.SubElement(entry, "token")
            token.set("type", "token")
            token.text = token_value
       
 
        return entry
    
    def create_battle(self, encounter):
        """Create a battle element from an encounter"""
        battle_id = self.get_next_id()
        battle = ET.Element(battle_id)
        
        # Store ID in encounter for cross-referencing
        encounter['_id'] = battle_id
        self.loader.name_to_id['encounter'][encounter['name']] = battle_id
        
        # Experience points
        exp = ET.SubElement(battle, 'exp')
        exp.set('type', 'number')
        exp.text = str(encounter.get('exp', 0))
        
        # Name
        name = ET.SubElement(battle, 'name')
        name.set('type', 'string')
        name.text = encounter['name']
        
        # NPC list
        npclist = ET.SubElement(battle, 'npclist')
        
        for npc_ref in encounter.get('npcs', []):
            self.create_npc_list_entry(npc_ref, npclist)
        
        return battle
    
    def generate(self):
        """Generate the complete <battle> section"""
        if not self.loader.encounters:
            return None
        
        if self.verbose:
            print(f"  Generating {len(self.loader.encounters)} battles...")
        
        # Create root battle element
        battle_root = ET.Element('battle')
        
        # Create each battle
        for encounter in self.loader.encounters:
            battle = self.create_battle(encounter)
            # Append to root by copying children
            for child in battle:
                battle_root.append(child)
            # But we need the battle wrapped in its ID tag
            # So actually we need to create the structure properly
        
        # Actually, let me restructure this properly
        # The XML structure is:
        # <battle>
        #   <id-00001>
        #     <name>...</name>
        #     <exp>...</exp>
        #     <npclist>...</npclist>
        #   </id-00001>
        #   <id-00002>...</id-00002>
        # </battle>
        
        battle_root = ET.Element('battle')
        
        for encounter in self.loader.encounters:
            battle_id = self.get_next_id()
            battle_entry = ET.SubElement(battle_root, battle_id)
            
            # Store ID for cross-referencing
            encounter['_id'] = battle_id
            self.loader.name_to_id['encounter'][encounter['name']] = battle_id
            
            # Experience
            exp = ET.SubElement(battle_entry, 'exp')
            exp.set('type', 'number')
            exp.text = str(encounter.get('exp', 0))
            
            # Name
            name = ET.SubElement(battle_entry, 'name')
            name.set('type', 'string')
            name.text = encounter['name']
            
            # NPC list
            npclist = ET.SubElement(battle_entry, 'npclist')
            
            for npc_ref in encounter.get('npcs', []):
                self.create_npc_list_entry(npc_ref, npclist)
        
        if self.verbose:
            print(f"  [OK] Generated {len(self.loader.encounters)} battles")
        
        return battle_root
    
    def to_xml_string(self, root):
        """Convert element tree to formatted XML string"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
