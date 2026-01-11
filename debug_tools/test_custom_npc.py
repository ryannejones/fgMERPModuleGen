#!/usr/bin/env python3
"""Test custom NPC creation"""

import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, 'data')

from library import ReferenceLibrary

# Load library
print("Loading library...")
lib = ReferenceLibrary()
print("Library loaded\n")

# Test creating Gardagd
print("=" * 60)
print("Test: create_custom_npc('Gardagd', 'Ranger', level=7)")
print("=" * 60)
result = lib.create_custom_npc(
    'Gardagd',
    'Ranger',
    level=7,
    modifications={
        'hits': {'@type': 'number', '_text': '60'}
    }
)

print(f"success: {result.get('success')}")
print(f"error: {result.get('error')}")
print(f"based_on: {result.get('based_on')}")
if result.get('entry'):
    print(f"entry name: {result['entry'].get('_display_name')}")
print()

# Test what the matcher finds
print("=" * 60)
print("Test: find_npc('Ranger', level=7)")
print("=" * 60)
match_result = lib.find_npc('Ranger', level=7)
print(f"found: {match_result.get('found')}")
print(f"matched_name: {match_result.get('matched_name')}")
print(f"method: {match_result.get('method')}")
