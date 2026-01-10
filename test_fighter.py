#!/usr/bin/env python3
"""Test what find_npc returns for Fighter"""

import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, 'data')

from library import ReferenceLibrary

# Load library
print("Loading library...")
lib = ReferenceLibrary()
print("Library loaded\n")

# Test Fighter with level 3
print("=" * 60)
print("Test: find_npc('Fighter', level=3)")
print("=" * 60)
result = lib.find_npc('Fighter', level=3)

print(f"found: {result.get('found')}")
print(f"suggestions: {result.get('suggestions')}")
print(f"method: {result.get('method')}")
print(f"matched_name: {result.get('matched_name')}")
print()

# Test Fighter without level
print("=" * 60)
print("Test: find_npc('Fighter')")
print("=" * 60)
result = lib.find_npc('Fighter')

print(f"found: {result.get('found')}")
print(f"suggestions: {result.get('suggestions')}")
print(f"method: {result.get('method')}")
print(f"matched_name: {result.get('matched_name')}")
